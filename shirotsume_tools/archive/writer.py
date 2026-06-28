from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from . import crypt


@dataclass(frozen=True)
class PackEntry:
    name: str
    data: bytes
    crypt_type: int = 1


def read_pack(path: str | Path) -> tuple[bytes, list[PackEntry]]:
    with open(path, "rb") as f:
        try:
            unpacker = crypt.unpack(f)
        except (crypt.InvalidSignatureError, crypt.UnsupportedVersionError) as exc:
            raise ValueError(str(exc)) from exc
        header = unpacker.header
        entries = [PackEntry(e.name, e.data, crypt_type=unpacker.entries[i].crypt_type()) for i, e in enumerate(unpacker)]
    return header, entries


def write_pack(path: str | Path, header: bytes, entries: Iterable[PackEntry], *, compress: bool = True) -> None:
    with open(path, "wb") as f:
        crypt.pack(f, header, [crypt.PackEntry(e.name, e.data) for e in entries], compress=compress)


def replace_entries(
    dat_path: str | Path,
    out_path: str | Path,
    replacements: Mapping[str, bytes] | Callable[[str], bytes | None],
    *,
    compress: bool = True,
) -> None:
    is_mapping = isinstance(replacements, Mapping)
    missing = set(replacements) if is_mapping else set()
    with open(dat_path, "rb") as fin, open(out_path, "wb") as fout:
        # Verify targets exist by reading table first
        try:
            unpacker = crypt.unpack(fin)
        except (crypt.InvalidSignatureError, crypt.UnsupportedVersionError) as exc:
            raise ValueError(str(exc)) from exc
        if is_mapping:
            for entry in unpacker.entries:
                if entry.name() in missing:
                    missing.remove(entry.name())
            if missing:
                raise KeyError(f"replacement target(s) not found: {', '.join(sorted(missing))}")
        fin.seek(0)
        try:
            crypt.replace(fin, fout, replacements, compress=compress)
        except (crypt.InvalidSignatureError, crypt.UnsupportedVersionError) as exc:
            raise ValueError(str(exc)) from exc
