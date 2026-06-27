import os
from typing import BinaryIO, Final

class Decryptor:
    version: Final[int]
    header: Final[bytes]
    file_count: Final[int]

    def _read_sig(self, dat_file: BinaryIO) -> bool: ...
    def _read_version(self, dat_file: BinaryIO) -> None: ...
    def _read_header(self, dat_file: BinaryIO) -> None: ...
    def _read_file_list(self, dat_file: BinaryIO) -> None: ...
    def load(self, dat_file: BinaryIO) -> None: ...
    def dump_file(
        self,
        dat_file: BinaryIO,
        file: str | int,
        outdir: str | os.PathLike[str],
        *,
        encoding: str | None = None,
    ) -> None: ...
    def dump(
        self,
        dat_file: BinaryIO,
        outdir: str | os.PathLike[str],
        *,
        encoding: str | None = None,
    ) -> None: ...
    @classmethod
    def decrypt(
        cls,
        dat_file: str | os.PathLike[str] | BinaryIO,
        outdir: str | os.PathLike[str],
        *,
        encoding: str | None = None,
    ) -> None: ...
    @property
    def file_list(self) -> list[str]: ...

    @property
    def headers(self) -> list[dict]: ...


decrypt = Decryptor.decrypt


class DecryptError(Exception):
    pass
