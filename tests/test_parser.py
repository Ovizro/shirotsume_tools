
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
