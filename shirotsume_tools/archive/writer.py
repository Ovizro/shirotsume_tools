from __future__ import annotations

import struct
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

SIG = b"RepiPack"
VERSION = 2
HEADER_KEY = 0x837FC07A
FILE_KEY = 0xF517AA26


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes
    crypt_type: int = 1


def _crypt_words(data: bytes, key: int) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0]
        struct.pack_into("<I", buf, offset, value ^ key)
        rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFF) ^ 0x98FCDBA2
        key = (key + rotated) & 0xFFFFFFFF
    return bytes(buf)


def _decrypt_words(data: bytes, key: int) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0] ^ key
        struct.pack_into("<I", buf, offset, value)
        rotated = (((value << 16) | (value >> 16)) & 0xFFFFFFFF) ^ 0x98FCDBA2
        key = (key + rotated) & 0xFFFFFFFF
    return bytes(buf)


def _file_decrypt(data: bytes) -> bytes:
    buf = bytearray(data)
    for offset in range(0, len(buf) - (len(buf) % 4), 4):
        value = struct.unpack_from("<I", buf, offset)[0]
        value = (value << 6) ^ (((value << 6) ^ ((value ^ 0x9B9B9B9B) >> 2)) & 0x3F3F3F3F)
        struct.pack_into("<I", buf, offset, value & 0xFFFFFFFF)
    return bytes(buf)


def _decompress(comp: bytes, size: int) -> bytes:
    out = bytearray()
    cache = bytearray(0x1000)
    cache_ptr = 0xFEE
    cursor = 0
    read_mask = 0
    mask = 0
    while len(out) < size:
        if read_mask == 0:
            read_mask = 0xFF
            mask = comp[cursor]
            cursor += 1
        if mask & 1:
            value = comp[cursor]
            cursor += 1
            out.append(value)
            cache[cache_ptr] = value
            cache_ptr = (cache_ptr + 1) & 0xFFF
        else:
            byte_0 = comp[cursor]
            byte_1 = comp[cursor + 1]
            cursor += 2
            offset = ((byte_1 & 0xF0) << 4) | byte_0
            length = (byte_1 & 0x0F) + 3
            for i in range(length):
                value = cache[(offset + i) & 0xFFF]
                out.append(value)
                cache[cache_ptr] = value
                cache_ptr = (cache_ptr + 1) & 0xFFF
                if len(out) == size:
                    break
        read_mask >>= 1
        mask >>= 1
    return bytes(out)


def _read_exact(file: BinaryIO, size: int) -> bytes:
    data = file.read(size)
    if len(data) != size:
        raise EOFError("unexpected end of RepiPack file")
    return data


def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with Path(path).open("rb") as file:
        if _read_exact(file, 8) != SIG:
            raise ValueError("not a RepiPack file")
        version = struct.unpack("<I", _read_exact(file, 4))[0]
        if version != VERSION:
            raise ValueError(f"unsupported RepiPack version {version}")
        header_size = struct.unpack("<I", _read_exact(file, 4))[0]
        header = _decrypt_words(_read_exact(file, header_size), HEADER_KEY)
        file_count = struct.unpack("<I", _read_exact(file, 4))[0]

        table = []
        for _ in range(file_count):
            raw = _decrypt_words(_read_exact(file, 80), FILE_KEY)
            name = raw[:0x40].split(b"\0", 1)[0].decode("cp932")
            offset, size, comp_size = struct.unpack_from("<III", raw, 0x40)
            crypt_type = raw[0x4C]
            table.append((name, offset, size, comp_size, crypt_type))

        entries: list[PackEntry] = []
        for name, offset, size, comp_size, crypt_type in table:
            file.seek(offset)
            data = _read_exact(file, comp_size)
            if crypt_type == 1:
                data = _decrypt_words(data, FILE_KEY)
            elif crypt_type == 2:
                data = _file_decrypt(data)
            if comp_size != size:
                data = _decompress(data, size)
            entries.append(PackEntry(name=name, data=data, crypt_type=crypt_type))

    return header, entries


def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry]) -> None:
    entries = list(entries)
    table_offset = 8 + 4 + 4 + len(header) + 4
    data_offset = table_offset + len(entries) * 80
    offset = data_offset
    table = bytearray()
    bodies = []

    for entry in entries:
        name = entry.name.encode("cp932")
        if len(name) >= 0x40:
            raise ValueError(f"packed name is too long: {entry.name}")
        body = _crypt_words(entry.data, FILE_KEY)
        raw = bytearray(80)
        raw[:len(name)] = name
        struct.pack_into("<III", raw, 0x40, offset, len(entry.data), len(body))
        raw[0x4C] = 1
        table.extend(_crypt_words(bytes(raw), FILE_KEY))
        bodies.append(body)
        offset += len(body)

    with Path(path).open("wb") as file:
        file.write(SIG)
        file.write(struct.pack("<I", VERSION))
        file.write(struct.pack("<I", len(header)))
        file.write(_crypt_words(header, HEADER_KEY))
        file.write(struct.pack("<I", len(entries)))
        file.write(table)
        for body in bodies:
            file.write(body)


def replace_entries(dat_path: str | Path, out_path: str | Path, replacements: Mapping[str, bytes]) -> None:
    header, entries = read_pack(dat_path)
    missing = set(replacements)
    patched = []
    for entry in entries:
        data = replacements.get(entry.name, entry.data)
        if entry.name in replacements:
            missing.remove(entry.name)
        patched.append(PackEntry(entry.name, data, 1))
    if missing:
        raise KeyError(f"replacement target(s) not found: {', '.join(sorted(missing))}")
    write_pack(out_path, header, patched)
