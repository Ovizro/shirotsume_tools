from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, MutableMapping
from pathlib import Path

CP932 = "cp932"


def jis_private_codes() -> Iterable[int]:
    for lead in range(0xF0, 0xFA):
        for trail in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            yield (lead << 8) | trail


def load_mapping(path: str | Path | None) -> dict[str, int]:
    if path is None or not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    mapping: dict[str, int] = {}
    for char, value in data.items():
        if isinstance(value, str):
            mapping[char] = int(value, 16)
        else:
            mapping[char] = int(value)
    return mapping


def save_mapping(path: str | Path, mapping: Mapping[str, int]) -> None:
    data = {char: f"{code:04X}" for char, code in sorted(mapping.items(), key=lambda item: item[1])}
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def encode_text(text: str, mapping: MutableMapping[str, int] | None = None) -> bytes:
    result = bytearray()
    available_codes = None
    if mapping is not None:
        used = set(mapping.values())
        available_codes = (code for code in jis_private_codes() if code not in used)

    for char in text:
        try:
            result.extend(char.encode(CP932))
            continue
        except UnicodeEncodeError:
            pass

        if mapping is None:
            raise UnicodeEncodeError(CP932, char, 0, 1, "character has no custom mapping")

        code = mapping.get(char)
        if code is None:
            assert available_codes is not None
            code = next(available_codes)
            mapping[char] = code
        result.append((code >> 8) & 0xFF)
        result.append(code & 0xFF)

    return bytes(result)


def encode_script_text(text: str, mapping: MutableMapping[str, int] | None = None) -> bytes:
    return encode_text(text, mapping)
