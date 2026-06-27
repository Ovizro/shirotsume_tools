
from shirotsume_tools.parser import parse_script
from shirotsume_tools.parser.model import TextEntry

SAMPLE_SCRIPT = '''\
// comment
page TestPage {
CreateBalloon("speaker", "hello world");
AddText("window", "second line");
CreateBalloonEx("a", "b", "c", "ex text", "e", "f", "g");
}
'''


def test_parse_script_extracts_text(tmp_path):
    script = tmp_path / "test.txt"
    script.write_text(SAMPLE_SCRIPT, encoding="utf-8")
    entries = parse_script(str(script))
    assert len(entries) == 3
    assert entries[0].text == "hello world"
    assert entries[1].text == "second line"
    assert entries[2].text == "ex text"
    assert entries[0].file_path == str(script)
    assert all(isinstance(e, TextEntry) for e in entries)


def test_parse_directory(tmp_path):
    (tmp_path / "a.txt").write_text('page A { CreateBalloon("x", "one"); }')
    (tmp_path / "b.txt").write_text('page B { AddText("y", "two"); }')
    from shirotsume_tools.parser import parse_directory
    entries = parse_directory(str(tmp_path))
    assert len(entries) == 2
    assert {e.text for e in entries} == {"one", "two"}


from shirotsume_tools.parser import parse_script_text

FIVE_FUNC_SCRIPT = '''\
page TestPage {
CreateBalloon("a", "balloon text");
CreateBalloonEx("a", "b", "c", "ex text", "e", "f", "g");
CreateBalloonBie("a", "bie text");
CreateText("text content");
AddText("win", "add text");
}
'''


def test_parse_script_text_extracts_all_five_functions():
    entries = parse_script_text(FIVE_FUNC_SCRIPT, file_path="test.txt")
    assert len(entries) == 5
    assert entries[0].text == "balloon text"
    assert entries[1].text == "ex text"
    assert entries[2].text == "bie text"
    assert entries[3].text == "text content"
    assert entries[4].text == "add text"
    assert all(e.file_path == "test.txt" for e in entries)


def test_parse_script_text_sets_start_stop():
    entries = parse_script_text('page T { CreateBalloon("x", "hi"); }', file_path="t.txt")
    assert len(entries) == 1
    assert entries[0].start < entries[0].stop
    assert entries[0].line >= 1
