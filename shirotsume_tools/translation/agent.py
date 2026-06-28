from __future__ import annotations

import csv
import json
import os
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from ..parser import TextEntry, parse_directory
from .patch import patch_script_file

DEFAULT_MEMORY: dict[str, Any] = {
    "glossary": {},
    "characters": {},
    "style": [
        "Translate Japanese visual novel dialogue into natural Simplified Chinese.",
        "Preserve script tags, markup, escapes, variables, and line breaks exactly unless they are human-readable prose.",
        "Keep recurring names, places, items, and special terms consistent with the glossary.",
    ],
    "decisions": [],
    "pending_suggestions": [],
}


def extract_translation_items(
    script_dir: str | Path, *, source_encoding: str = "cp932", limit: int | None = None,
) -> list[TextEntry]:
    script_root = Path(script_dir).resolve()
    entries = parse_directory(str(script_root), encoding=source_encoding)
    result: list[TextEntry] = []
    for entry in entries:
        try:
            rel = Path(entry.file_path).relative_to(script_root).as_posix()
        except ValueError:
            rel = entry.file_path
        result.append(entry.model_copy(update={"file_path": rel}))
    if limit is not None:
        result = result[:limit]
    return result


def chunked_by_budget(items: Sequence[TextEntry], max_items: int, max_source_chars: int) -> Iterable[Sequence[TextEntry]]:
    batch: list[TextEntry] = []
    char_count = 0
    for item in items:
        item_chars = len(item.text)
        if batch and (len(batch) >= max_items or char_count + item_chars > max_source_chars):
            yield batch
            batch = []
            char_count = 0
        batch.append(item)
        char_count += item_chars
    if batch:
        yield batch


def _response_text(response: object) -> str:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text:
        return text
    return str(response)


def _json_object_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def load_translation_memory(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return dict(DEFAULT_MEMORY)
    memory_path = Path(path)
    if not memory_path.exists():
        return dict(DEFAULT_MEMORY)
    loaded = json.loads(memory_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Translation memory must be a JSON object: {memory_path}")
    memory = dict(DEFAULT_MEMORY)
    memory.update(loaded)
    for key in ("glossary", "characters"):
        if not isinstance(memory.get(key), dict):
            raise ValueError(f"Translation memory field must be an object: {key}")
    for key in ("style", "decisions", "pending_suggestions"):
        if not isinstance(memory.get(key), list):
            raise ValueError(f"Translation memory field must be a list: {key}")
    return memory


def save_translation_memory(path: str | Path, memory: dict[str, Any]) -> None:
    memory_path = Path(path)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _proposal_key(proposal: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(proposal.get("type", "")),
        str(proposal.get("source", "")),
        str(proposal.get("target", "")),
    )


def merge_memory_suggestions(memory: dict[str, Any], suggestions: Sequence[dict[str, Any]]) -> int:
    pending = memory.setdefault("pending_suggestions", [])
    if not isinstance(pending, list):
        pending = []
        memory["pending_suggestions"] = pending

    seen = {_proposal_key(item) for item in pending if isinstance(item, dict)}
    added = 0
    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            continue
        proposal = {
            "type": str(suggestion.get("type", "decision")),
            "source": str(suggestion.get("source", "")),
            "target": str(suggestion.get("target", "")),
            "note": str(suggestion.get("note", "")),
        }
        if not proposal["source"] and not proposal["target"] and not proposal["note"]:
            continue
        key = _proposal_key(proposal)
        if key in seen:
            continue
        pending.append(proposal)
        seen.add(key)
        added += 1
    return added


def translation_system_prompt(prompt_language: str = "en") -> str:
    if prompt_language.lower() in {"zh", "cn", "chinese", "zh-cn"}:
        return (
            "你正在把日文视觉小说游戏脚本翻译成简体中文。\n"
            "在写出译文前，请在内部仔细判断当前场景、说话者意图、情绪语气、上下文承接和自然中文表达。"
            "这些思考只用于生成译文；JSON 输出中不要包含分析、注释、备选译法或解释。\n"
            "\n"
            "翻译记忆具有约束力：\n"
            "- 人名、地名、物品、组织、专有名词必须严格遵守 glossary。\n"
            "- 角色称呼、语气、口癖、关系距离必须遵守 characters。\n"
            "- 在做新选择前，优先遵守 style 和 decisions。\n"
            "- 如果你认为已有术语决定不合适，不要在译文中擅自改写；请放入 memory_suggestions。\n"
            "\n"
            "脚本安全规则：\n"
            "- 必须保留标签、标记、转义、变量、类似命令的片段、引擎需要的标点和换行。\n"
            "- 必须原样保留纯标点演出片段，尤其是 <TYPE interval=60>･･････</TYPE> 这样的定时停顿。\n"
            "- 只翻译 source_text 中给玩家阅读的自然语言文本。\n"
            "- 每条输出都必须能直接替换对应的原文字符串。\n"
            "- 把同一文件中按顺序排列的 items 当成连续场景来理解，保持相邻条目的叙事连续性。\n"
            "- 不要生硬照搬日语语法、身体部位惯用表达、省略号和句尾；中文自然表达优先。\n"
            "- 标签必须保留在相对于其作用文本的原始位置。不要删除或翻译标签名和属性。\n"
            "- 文风应是润色后的中文视觉小说叙事和对白，而不是字典式直译。\n"
            "\n"
            "记忆更新规则：\n"
            "- 每批都主动检查是否有值得记录的长期决定；如果有，请返回 1 到 5 条 suggestions。\n"
            "- 合适的建议包括角色/姓名译名、称呼方式、研究机构、反复出现的地点/物品、专有术语和文风决定。\n"
            "- 不要为一次性普通短语添加建议。\n"
            "- 不要重复 memory 中已经存在的建议。\n"
            "- 如果本批确实没有可复用决定，memory_suggestions 可以为空数组。\n"
            "\n"
            "只返回如下形状的 JSON：\n"
            "{"
            '"translations":[{"id":"same id","text":"translated Chinese text"}],'
            '"memory_suggestions":[{"type":"glossary|character|style|decision",'
            '"source":"Japanese term or topic","target":"Chinese decision","note":"short reason"}]'
            "}."
        )

    return (
        "You are translating Japanese visual novel game scripts into Simplified Chinese.\n"
        "Think through the local scene context, speaker intent, emotional tone, "
        "and idiomatic Chinese phrasing before writing each translation. "
        "Do this reasoning internally; do not include analysis, notes, alternatives, or explanations in the JSON output.\n"
        "\n"
        "Translation memory is binding:\n"
        "- Follow glossary entries exactly for names, places, items, organizations, and special terms.\n"
        "- Follow character notes for pronouns, speech register, catchphrases, and relationship tone.\n"
        "- Follow style and decisions before making new choices.\n"
        "- If a glossary decision seems wrong, do not override it in the translation. Add a suggestion instead.\n"
        "\n"
        "Script safety rules:\n"
        "- Preserve tags, markup, escapes, variables, command-like fragments, "
        "punctuation required by the engine, and line breaks.\n"
        "- Preserve punctuation-only display fragments exactly, "
        "especially timed pauses such as <TYPE interval=60>･･････</TYPE>.\n"
        "- Translate only human-readable prose inside source_text.\n"
        "- Keep each output line usable as a direct replacement for the corresponding source string.\n"
        "- Use ordered items in each file as one continuous scene; preserve continuity across adjacent entries.\n"
        "- Avoid stiff literal translations of Japanese grammar, body-part idioms, "
        "ellipses, and sentence endings when natural Chinese would phrase them differently.\n"
        "- Keep tags at their original positions relative to the text they affect. "
        "Do not delete or translate tag names or attributes.\n"
        "- Prefer polished visual-novel narration and dialogue over dictionary-literal wording.\n"
        "\n"
        "Memory update rules:\n"
        "- Actively check every batch for durable decisions worth recording; if any exist, return 1 to 5 suggestions.\n"
        "- Good suggestions include character/name translations, forms of address, "
        "research groups, recurring places/items, special terminology, and style decisions.\n"
        "- Do not suggest one-off ordinary phrases.\n"
        "- Do not repeat suggestions already present in memory.\n"
        "- If the batch truly has no reusable decisions, memory_suggestions may be an empty array.\n"
        "\n"
        "Return only JSON with this exact shape:\n"
        "{"
        '"translations":[{"id":"same id","text":"translated Chinese text"}],'
        '"memory_suggestions":[{"type":"glossary|character|style|decision",'
        '"source":"Japanese term or topic","target":"Chinese decision","note":"short reason"}]'
        "}."
    )


def translate_batch(
    batch: Sequence[TextEntry],
    *,
    model: str,
    target_language: str,
    memory: dict[str, Any],
    story_context: str = "",
    temperature: float = 0.2,
    api_base_url: str | None = None,
    prompt_language: str = "en",
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the OpenAI SDK first: pip install shirotsume_tools[translation]") from exc

    client_kwargs: dict[str, str] = {}
    if api_base_url:
        client_kwargs["base_url"] = api_base_url
    client = OpenAI(**client_kwargs)
    payload = {
        "target_language": target_language,
        "story_context": story_context,
        "translation_memory": memory,
        "memory_instruction": (
            "After translating, propose durable glossary/character/style/decision updates for recurring names, "
            "terms, organizations, forms of address, or style choices found in this batch. "
            "Return 1 to 5 memory_suggestions when useful; return [] only when there is truly nothing reusable."
        ),
        "items": [
            {
                "id": f"{item.file_path}#{i}",
                "file": item.file_path,
                "index": i,
                "line": item.line,
                "source_text": item.text,
            }
            for i, item in enumerate(batch)
        ],
    }
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": translation_system_prompt(prompt_language)},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=temperature,
    )
    data = _json_object_from_response(_response_text(response))
    translations = data.get("translations")
    if not isinstance(translations, list):
        raise ValueError("OpenAI response did not contain a translations list")
    id_to_source = {f"{item.file_path}#{i}": item.text for i, item in enumerate(batch)}
    result: dict[str, str] = {}
    for entry in translations:
        if not isinstance(entry, dict) or "id" not in entry or "text" not in entry:
            raise ValueError(f"Invalid translation entry: {entry!r}")
        source = id_to_source.get(str(entry["id"]))
        if source is None:
            raise ValueError(f"Unknown translation id: {entry['id']!r}")
        result[source] = str(entry["text"])
    suggestions = data.get("memory_suggestions", [])
    if not isinstance(suggestions, list):
        raise ValueError("OpenAI response memory_suggestions must be a list")
    return result, [item for item in suggestions if isinstance(item, dict)]


def translate_batch_with_retry(
    batch: Sequence[TextEntry],
    *,
    model: str,
    target_language: str,
    memory: dict[str, Any],
    story_context: str = "",
    temperature: float = 0.2,
    api_base_url: str | None = None,
    prompt_language: str = "en",
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    try:
        return translate_batch(
            batch,
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
    except Exception:
        if len(batch) <= 1:
            raise
        midpoint = len(batch) // 2
        left_translations, left_suggestions = translate_batch_with_retry(
            batch[:midpoint],
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        right_translations, right_suggestions = translate_batch_with_retry(
            batch[midpoint:],
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        left_translations.update(right_translations)
        return left_translations, left_suggestions + right_suggestions


def write_replacement_csv(path: str | Path, rows: Sequence[tuple[str, str]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["raw_text", "text", "comment"])
        writer.writeheader()
        for raw_text, text in rows:
            writer.writerow({"raw_text": raw_text, "text": text, "comment": ""})


def read_existing_replacement_csv(path: str | Path) -> dict[str, tuple[str, str]]:
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or "raw_text" not in reader.fieldnames:
            return {}
        existing: dict[str, tuple[str, str]] = {}
        for row in reader:
            raw_text = row.get("raw_text", "")
            if not raw_text:
                continue
            existing[raw_text] = (row.get("text", ""), row.get("comment", ""))
        return existing


def write_merged_replacement_csv(path: str | Path, raw_texts: Sequence[str], translations: Mapping[str, str]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_existing_replacement_csv(path)
    added = 0
    seen: set[str] = set()
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["raw_text", "text", "comment"])
        writer.writeheader()
        for raw_text in raw_texts:
            if raw_text in seen:
                continue
            seen.add(raw_text)
            previous = existing.get(raw_text)
            if previous is None:
                added += 1
                text = translations.get(raw_text, "")
                comment = ""
            else:
                text, comment = previous
                if raw_text in translations:
                    text = translations[raw_text]
            writer.writerow({"raw_text": raw_text, "text": text, "comment": comment})
    return added


def sync_translation_csvs(
    script_dir: str | Path,
    replacements_dir: str | Path,
    *,
    source_encoding: str = "cp932",
) -> int:
    script_root = Path(script_dir)
    replacements_root = Path(replacements_dir)
    items = extract_translation_items(script_root, source_encoding=source_encoding)
    by_file: dict[str, list[str]] = {}
    for item in items:
        by_file.setdefault(item.file_path, []).append(item.text)

    added = 0
    for relative_file, raw_texts in by_file.items():
        csv_path = replacements_root / Path(relative_file).with_suffix(".csv")
        added += write_merged_replacement_csv(csv_path, raw_texts, {})
    return added


def translate_scripts(
    script_dir: str | Path,
    replacements_dir: str | Path,
    *,
    patched_dir: str | Path | None = None,
    mapping_path: str | Path | None = None,
    model: str | None = None,
    target_language: str = "Simplified Chinese",
    source_encoding: str = "cp932",
    batch_size: int = 24,
    limit: int | None = None,
    story_context: str = "",
    temperature: float = 0.2,
    memory_path: str | Path | None = None,
    api_base_url: str | None = None,
    prompt_language: str = "en",
    max_source_chars: int = 6000,
) -> int:
    model = model or os.environ.get("OPENAI_MODEL", "gpt-4.1")
    script_root = Path(script_dir)
    replacements_root = Path(replacements_dir)
    items = extract_translation_items(script_root, source_encoding=source_encoding, limit=limit)
    memory = load_translation_memory(memory_path)

    existing_by_file: dict[str, dict[str, tuple[str, str]]] = {}
    existing_translations: dict[str, str] = {}
    missing_items: list[TextEntry] = []
    for item in items:
        existing = existing_by_file.get(item.file_path)
        if existing is None:
            csv_path = replacements_root / Path(item.file_path).with_suffix(".csv")
            existing = read_existing_replacement_csv(csv_path)
            existing_by_file[item.file_path] = existing
        previous = existing.get(item.text)
        if previous is not None and previous[0]:
            existing_translations[item.text] = previous[0]
        else:
            missing_items.append(item)

    translations: dict[str, str] = dict(existing_translations)
    for batch in chunked_by_budget(missing_items, batch_size, max_source_chars):
        batch_translations, suggestions = translate_batch_with_retry(
            batch,
            model=model,
            target_language=target_language,
            memory=memory,
            story_context=story_context,
            temperature=temperature,
            api_base_url=api_base_url,
            prompt_language=prompt_language,
        )
        translations.update(batch_translations)
        if merge_memory_suggestions(memory, suggestions) and memory_path is not None:
            save_translation_memory(memory_path, memory)

    by_file: dict[str, list[str]] = {}
    for item in items:
        if item.text not in translations:
            raise ValueError(f"Missing translation for {item.file_path}")
        by_file.setdefault(item.file_path, []).append(item.text)

    for relative_file, raw_texts in by_file.items():
        relative_path = Path(relative_file)
        csv_path = replacements_root / relative_path.with_suffix(".csv")
        write_merged_replacement_csv(csv_path, raw_texts, translations)
        if patched_dir is not None:
            source_path = script_root / relative_path
            out_path = Path(patched_dir) / relative_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            patch_script_file(source_path, csv_path, out_path, source_encoding=source_encoding, mapping_path=mapping_path)

    if memory_path is not None:
        save_translation_memory(memory_path, memory)

    return len(items)
