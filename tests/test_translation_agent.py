import json
from unittest.mock import MagicMock, patch

from shirotsume_tools.translation.agent import (
    extract_translation_items,
    sync_translation_csvs,
    translate_batch,
    translate_scripts,
)

SAMPLE_SCRIPT = '''page T {
CreateBalloon("x", "テスト");
}'''

MULTI_SPAN_SCRIPT = '''page T {
CreateBalloon("x", "テスト1");
CreateBalloon("x", "テスト2");
CreateBalloon("x", "テスト3");
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
    assert translations == {"こんにちは": "你好"}
    assert suggestions == []


def test_translate_scripts_multi_batch(tmp_path):
    """Verify translate_scripts handles multiple batches without id collisions."""
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    (script_dir / "1-01.txt").write_text(MULTI_SPAN_SCRIPT, encoding="cp932")

    repl_dir = tmp_path / "translations"

    responses = [
        MagicMock(output_text=json.dumps({
            "translations": [
                {"id": "1-01.txt#0", "text": "测试1"},
                {"id": "1-01.txt#1", "text": "测试2"},
            ],
            "memory_suggestions": [],
        })),
        MagicMock(output_text=json.dumps({
            "translations": [
                {"id": "1-01.txt#0", "text": "测试3"},
            ],
            "memory_suggestions": [],
        })),
    ]

    mock_module = MagicMock()
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = responses
    mock_module.OpenAI.return_value = mock_client

    with patch.dict("sys.modules", {"openai": mock_module}):
        count = translate_scripts(
            str(script_dir), str(repl_dir),
            model="gpt-4.1", batch_size=2, source_encoding="cp932",
        )

    assert count == 3
    csv_path = repl_dir / "1-01.csv"
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "测试1" in content
    assert "测试2" in content
    assert "测试3" in content


def test_translate_scripts_incremental(tmp_path):
    """Verify translate_scripts skips items with existing translations."""
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    (script_dir / "1-01.txt").write_text(MULTI_SPAN_SCRIPT, encoding="cp932")

    repl_dir = tmp_path / "translations"
    repl_dir.mkdir()
    (repl_dir / "1-01.csv").write_text(
        "raw_text,text,comment\r\nテスト1,已翻译1,\r\n",
        encoding="utf-8-sig",
    )

    mock_response = MagicMock()
    mock_response.output_text = json.dumps({
        "translations": [
            {"id": "1-01.txt#0", "text": "测试2"},
            {"id": "1-01.txt#1", "text": "测试3"},
        ],
        "memory_suggestions": [],
    })
    mock_module = MagicMock()
    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_response
    mock_module.OpenAI.return_value = mock_client

    with patch.dict("sys.modules", {"openai": mock_module}):
        count = translate_scripts(
            str(script_dir), str(repl_dir),
            model="gpt-4.1", batch_size=24, source_encoding="cp932",
        )

    assert count == 3
    assert mock_client.responses.create.call_count == 1
    csv_path = repl_dir / "1-01.csv"
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "已翻译1" in content
    assert "测试2" in content
    assert "测试3" in content


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
