from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

from . import crypt


def read_pack(path: str | Path) -> tuple[bytes, list[crypt.PackEntry]]:
    with open(path, "rb") as f:
        try:
            unpacker = crypt.unpack(f)
        except (crypt.InvalidSignatureError, crypt.UnsupportedVersionError) as exc:
            raise ValueError(str(exc)) from exc
        header = unpacker.header
        entries = list(unpacker)
    return header, entries


def write_pack(
    path: str | Path,
    header: bytes,
    entries: Iterable[crypt.PackEntry],
    *,
    compress: bool = True,
    count: int | None = None,
) -> None:
    with open(path, "wb") as f:
        crypt.pack(f, header, entries, compress=compress, count=count)


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
