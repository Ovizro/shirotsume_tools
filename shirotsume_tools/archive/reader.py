from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO

from ._decrypt import DecryptError, Decryptor
from .errors import ArchiveError, InvalidSignatureError, UnsupportedVersionError
from .model import FileEntry


def _map_decrypt_error(source: DecryptError) -> ArchiveError:
    msg = str(source)
    if "not RepiPack" in msg:
        return InvalidSignatureError(msg)
    elif "unsupported version" in msg:
        return UnsupportedVersionError(msg)
    return ArchiveError(msg)


class Archive:
    """高层归档接口"""

    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._reader = Decryptor()
        self._file: BinaryIO | None = None

    def __enter__(self) -> "Archive":
        self._file = open(self._path, "rb")
        try:
            self._reader.load(self._file)
        except DecryptError as exc:
            self._file.close()
            raise _map_decrypt_error(exc) from exc
        except Exception as exc:
            self._file.close()
            cause = exc.__cause__ or exc.__context__
            if isinstance(cause, DecryptError):
                raise _map_decrypt_error(cause) from exc
            raise ArchiveError(f"failed to load archive {self._path}") from exc
        return self

    def __exit__(self, *args) -> None:
        if self._file is not None:
            self._file.close()

    @property
    def file_list(self) -> list[str]:
        return list(self._reader.file_list)

    @property
    def file_count(self) -> int:
        return self._reader.file_count

    def extract(self, file: str | int, outdir: str | Path,
                *, encoding: str | None = None) -> None:
        if self._file is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        index = self._resolve_index(file)
        self._reader.dump_file(self._file, index, str(outdir), encoding=encoding)

    def extract_all(self, outdir: str | Path,
                    *, encoding: str | None = None) -> None:
        if self._file is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        self._reader.dump(self._file, str(outdir), encoding=encoding)

    def iter_entries(self) -> Iterator[FileEntry]:
        headers = self._reader.headers
        for i, name in enumerate(self.file_list):
            h = headers[i]
            yield FileEntry(
                name=name,
                offset=h["offset"],
                size=h["size"],
                comp_size=h["comp_size"],
                crypt_type=h["crypt_type"],
            )

    def _resolve_index(self, file: str | int) -> int:
        if isinstance(file, int):
            return file
        return self.file_list.index(file)


def decrypt(dat_file: str | Path, outdir: str | Path,
            *, encoding: str | None = None) -> None:
    with Archive(dat_file) as arc:
        arc.extract_all(outdir, encoding=encoding)
