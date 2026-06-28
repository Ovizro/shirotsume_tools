from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from . import crypt


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes


def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with open(path, "rb") as f:
        unpacker = crypt.unpack(f)
        header = unpacker.header
        entries = [PackEntry(e.name, e.data) for e in unpacker]
    return header, entries


def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry], *, compress: bool = True) -> None:
    with open(path, "wb") as f:
        crypt.pack(f, header, [crypt.PackEntry(e.name, e.data) for e in entries], compress=compress)


def replace_entries(dat_path: str | Path, out_path: str | Path,
                    replacements: Mapping[str, bytes], *, compress: bool = True) -> None:
    missing = set(replacements)
    with open(dat_path, "rb") as fin, open(out_path, "wb") as fout:
        # Verify targets exist by reading table first
        unpacker = crypt.unpack(fin)
        for entry in unpacker.entries:
            if entry.name() in missing:
                missing.remove(entry.name())
        if missing:
            raise KeyError(f"replacement target(s) not found: {', '.join(sorted(missing))}")
        fin.seek(0)
        crypt.replace(fin, fout, replacements, compress=compress)
