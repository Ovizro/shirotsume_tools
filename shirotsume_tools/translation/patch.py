from __future__ import annotations

import csv
import json
from collections.abc import Mapping, Sequence
from io import StringIO
from pathlib import Path

from ..archive import replace_entries
from ..parser import parse_script_text
from .encoding import encode_script_text, load_mapping, save_mapping


def _escape_script_string(text: str) -> str:
    result = ['"']
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            if index + 1 < len(text):
                result.append(text[index : index + 2])
                index += 2
                continue
            result.append("\\")
        elif char == '"':
            result.append('\\"')
        elif char == "\n":
            result.append("\r\n")
        else:
            result.append(char)
        index += 1
    result.append('"')
    return "".join(result)


def normalize_replacement_text(text: str) -> str:
    """Normalize visible pause punctuation without touching script tags."""
    parts: list[str] = []
    in_tag = False
    buffer: list[str] = []

    def flush_visible() -> None:
        if not buffer:
            return
        visible = "".join(buffer)
        buffer.clear()

        output: list[str] = []
        index = 0
        pause_chars = {".", ",", "，", "、", "。", "･", "・", "·", "…"}
        while index < len(visible):
            char = visible[index]
            if char in pause_chars:
                start = index
                while index < len(visible) and visible[index] in pause_chars:
                    index += 1
                run = visible[start:index]
                if len(run) >= 2 and any(mark in run for mark in ("･", "・", "·", ".", "…")):
                    output.append("……")
                else:
                    output.append(run)
                continue
            output.append(char)
            index += 1

        normalized = "".join(output)
        normalized = normalized.replace("……。", "……")
        normalized = normalized.replace("……，", "……")
        normalized = normalized.replace("……、", "……")
        parts.append(normalized)

    for char in text:
        if char == "<":
            flush_visible()
            in_tag = True
            parts.append(char)
        elif char == ">" and in_tag:
            in_tag = False
            parts.append(char)
        elif in_tag:
            parts.append(char)
        else:
            buffer.append(char)
    flush_visible()
    return "".join(parts)


def load_replacements(path: str | Path) -> Sequence[str] | Mapping[str, str]:
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(item) for item in data]
        return {str(key): str(value) for key, value in data.items()}

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
    if not rows:
        return []
    fieldnames = reader.fieldnames or []
    if "raw_text" in fieldnames and "text" in fieldnames:
        return {row["raw_text"]: normalize_replacement_text(row["text"]) for row in rows if row.get("text")}
    if "text" in fieldnames:
        return [normalize_replacement_text(row["text"]) for row in rows]
    raise ValueError("replacement CSV must have a text column, or raw_text and text columns")


def patch_script_text(script: str, replacements: Sequence[str] | Mapping[str, str]) -> tuple[str, int]:
    entries = parse_script_text(script)
    edits: list[tuple[int, int, str]] = []
    if isinstance(replacements, Mapping):
        for entry in entries:
            replacement = replacements.get(entry.text)
            if replacement is not None:
                edits.append((entry.start, entry.stop, replacement))
    else:
        if len(replacements) > len(entries):
            raise ValueError(f"{len(replacements)} replacements provided for {len(entries)} script text spans")
        for entry, replacement in zip(entries, replacements, strict=False):
            edits.append((entry.start, entry.stop, replacement))

    if not edits:
        return script, 0

    patched = StringIO()
    cursor = 0
    for start, stop, replacement in edits:
        patched.write(script[cursor:start])
        patched.write(_escape_script_string(replacement))
        cursor = stop + 1
    patched.write(script[cursor:])
    return patched.getvalue(), len(edits)


def patch_script_file(
    script_path: str | Path,
    replacements_path: str | Path,
    out_path: str | Path,
    *,
    source_encoding: str = "cp932",
    mapping_path: str | Path | None = None,
) -> int:
    mapping = load_mapping(mapping_path)
    with Path(script_path).open("r", encoding=source_encoding, newline="") as file:
        script = file.read()
    patched, count = patch_script_text(script, load_replacements(replacements_path))
    encoded = encode_script_text(patched, mapping)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(encoded)
    if mapping_path is not None:
        save_mapping(mapping_path, mapping)
    return count


def patch_dat_script(
    dat_path: str | Path,
    script_name: str,
    patched_script_path: str | Path,
    out_dat: str | Path,
) -> None:
    replace_entries(dat_path, out_dat, {script_name: Path(patched_script_path).read_bytes()})
