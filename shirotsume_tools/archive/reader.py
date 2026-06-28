from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO

from . import crypt
from .errors import ArchiveError, InvalidSignatureError, UnsupportedVersionError
from .model import FileEntry


def _map_error(source: crypt.RepiPackError) -> ArchiveError:
    if isinstance(source, crypt.InvalidSignatureError):
        return InvalidSignatureError(str(source))
    if isinstance(source, crypt.UnsupportedVersionError):
        return UnsupportedVersionError(str(source))
    return ArchiveError(str(source))


class Archive:
    def __init__(self, path: str | Path):
        self._path = Path(path)
        self._file: BinaryIO | None = None
        self._unpacker: crypt.Unpacker | None = None
        self._entries: list[crypt.RawEntry] = []

    def __enter__(self) -> "Archive":
        self._file = self._path.open("rb")
        try:
            self._unpacker = crypt.unpack(self._file)
            self._entries = self._unpacker.entries
        except crypt.RepiPackError as exc:
            self._file.close()
            raise _map_error(exc) from exc
        return self

    def __exit__(self, *args) -> None:
        if self._file is not None:
            self._file.close()

    @property
    def file_list(self) -> list[str]:
        return [e.name() for e in self._entries]

    @property
    def file_count(self) -> int:
        return len(self._entries)

    def _resolve_entry(self, file: str | int) -> crypt.RawEntry:
        if isinstance(file, int):
            return self._entries[file]
        for entry in self._entries:
            if entry.name() == file:
                return entry
        raise KeyError(f"file not found: {file}")

    def extract(self, file: str | int, outdir: str | Path, *, encoding: str | None = None) -> None:
        if self._file is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        raw = self._resolve_entry(file)
        self._file.seek(raw.offset())
        comp_data = self._file.read(raw.comp_size())
        if len(comp_data) != raw.comp_size():
            raise ArchiveError("unexpected end of archive")
        data = crypt.decode_body(comp_data, raw.size(), raw.crypt_type())

        outpath = outdir / raw.name()
        outpath.parent.mkdir(parents=True, exist_ok=True)
        if encoding is not None and raw.name().endswith(".txt"):
            outpath.write_text(data.decode("MS932"), encoding=encoding)
        else:
            outpath.write_bytes(data)

    def extract_all(self, outdir: str | Path, *, encoding: str | None = None) -> None:
        if self._unpacker is None:
            raise RuntimeError("archive not opened; use 'with Archive(...)'")
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        for entry in self._unpacker:
            outpath = outdir / entry.name
            outpath.parent.mkdir(parents=True, exist_ok=True)
            if encoding is not None and entry.name.endswith(".txt"):
                outpath.write_text(entry.data.decode("MS932"), encoding=encoding)
            else:
                outpath.write_bytes(entry.data)

    def iter_entries(self) -> Iterator[FileEntry]:
        for raw in self._entries:
            yield FileEntry(
                name=raw.name(),
                offset=raw.offset(),
                size=raw.size(),
                comp_size=raw.comp_size(),
                crypt_type=raw.crypt_type(),
            )


def decrypt(dat_file: str | Path, outdir: str | Path, *, encoding: str | None = None) -> None:
    with Archive(dat_file) as arc:
        arc.extract_all(outdir, encoding=encoding)
