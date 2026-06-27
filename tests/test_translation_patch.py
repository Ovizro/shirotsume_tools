from shirotsume_tools.translation.patch import (
    patch_script_text, load_replacements, normalize_replacement_text,
)


SAMPLE = '''page T {
CreateBalloon("x", "こんにちは");
}'''


def test_patch_script_text_mapping():
    patched, count = patch_script_text(SAMPLE, {"こんにちは": "你好"})
    assert count == 1
    assert "你好" in patched
    assert "こんにちは" not in patched


def test_patch_script_text_sequence():
    patched, count = patch_script_text(SAMPLE, ["你好"])
    assert count == 1
    assert "你好" in patched


def test_patch_script_text_no_match():
    patched, count = patch_script_text(SAMPLE, {"不存在的文本": "x"})
    assert count == 0
    assert patched == SAMPLE


def test_patch_script_text_five_functions():
    script = '''page T {
CreateBalloon("a", "b1");
CreateBalloonEx("a","b","c","b2","d","e","f");
CreateBalloonBie("a", "b3");
CreateText("b4");
AddText("w", "b5");
}'''
    patched, count = patch_script_text(script, {"b1": "c1", "b2": "c2", "b3": "c3", "b4": "c4", "b5": "c5"})
    assert count == 5
    for c in ("c1", "c2", "c3", "c4", "c5"):
        assert c in patched


def test_load_replacements_csv_mapping(tmp_path):
    csv_path = tmp_path / "r.csv"
    csv_path.write_text("raw_text,text,comment\n原,译,\n", encoding="utf-8-sig")
    result = load_replacements(csv_path)
    assert result == {"原": "译"}


def test_normalize_replacement_text_pause():
    assert normalize_replacement_text("･･････") == "……"
