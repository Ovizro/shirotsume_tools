from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import BinaryIO, Iterable

from typing_extensions import Buffer


class RepiPackError(Exception):
    pass


class InvalidSignatureError(RepiPackError):
    pass


class UnsupportedVersionError(RepiPackError):
    pass


class ShortReadError(RepiPackError):
    pass


class DecompressionError(RepiPackError):
    pass


class CompressionError(RepiPackError):
    pass


class RawEntry:
    def name(self) -> str: ...
    def offset(self) -> int: ...
    def size(self) -> int: ...
    def comp_size(self) -> int: ...
    def crypt_type(self) -> int: ...


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes
    crypt_type: int = ...


def decode_table(data: Buffer) -> tuple[bytes, list[RawEntry]]: ...
def encode_table(header: Buffer, entries: list[RawEntry]) -> bytes: ...
def decode_body(comp_data: Buffer, size: int, crypt_type: int) -> bytes: ...
def encode_body(data: Buffer, compress: bool = True) -> tuple[bytes, int]: ...


class Unpacker:
    def __init__(self, file: BinaryIO | None = None) -> None: ...

    @property
    def header(self) -> bytes: ...

    @property
    def entries(self) -> list[RawEntry]: ...

    def __iter__(self) -> Unpacker: ...
    def __next__(self) -> PackEntry: ...


def unpack(file: BinaryIO) -> Unpacker: ...
def pack(file: BinaryIO, header: Buffer, entries: list[PackEntry], compress: bool = True) -> None: ...
def replace(
    in_file: BinaryIO,
    out_file: BinaryIO,
    replacements: Mapping[str, bytes | None] | Callable[[str], bytes | None],
    compress: bool = True,
) -> None: ...
