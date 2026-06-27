import json
from unittest.mock import MagicMock, patch

import pytest

from shirotsume_tools.translation.agent import (
    extract_translation_items, translate_batch, translate_scripts, sync_translation_csvs,
)


SAMPLE_SCRIPT = '''page T {
CreateBalloon("x", "テスト");
}'''


def test_extract_translation_items(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text(SAMPLE_SCRIPT, encoding="cp932")
    items = extract_translation_items(str(tmp_path), source_encoding="cp932")
    assert len(items) == 1
    assert items[0].text == "テスト"
    assert items[0].file_path.endswith("1-01.txt")


def test_translate_batch_monkeypatch(tmp_path):
    from shirotsume_tools.parser import TextEntry
    batch = [TextEntry(text="こんにちは", file_path="a.txt", line=1, start=0, stop=10)]
    mock_response = MagicMock()
    mock_response.output_text = json.dumps({
        "translations": [{"id": "a.txt#0", "text": "你好"}],
        "memory_suggestions": [],
    })
    mock_module = MagicMock()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_response
    mock_module.OpenAI.return_value = mock_client
    with patch.dict("sys.modules", {"openai": mock_module}):
        translations, suggestions = translate_batch(
            batch, model="gpt-4.1", target_language="Simplified Chinese",
            memory={"glossary": {}, "characters": {}, "style": [], "decisions": [], "pending_suggestions": []},
        )
    assert translations == {"a.txt#0": "你好"}
    assert suggestions == []


def test_sync_translation_csvs(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text(SAMPLE_SCRIPT, encoding="cp932")
    repl_dir = tmp_path / "translations"
    added = sync_translation_csvs(str(tmp_path), str(repl_dir), source_encoding="cp932")
    assert added >= 1
    csv_path = repl_dir / "1-01.csv"
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "テスト" in content
