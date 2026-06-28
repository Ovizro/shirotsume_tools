from shirotsume_tools.translation.encoding import (
    encode_text,
    jis_private_codes,
    load_mapping,
    save_mapping,
)


def test_encode_text_cp932_passthrough():
    assert encode_text("abc") == b"abc"


def test_encode_text_custom_mapping_assigns_new_code():
    # U+20BB7 (𠮷) is a CJK Extension B ideograph not representable in CP932,
    # so encode_text must assign it a JIS private-use code.
    char = "𠮷"
    mapping = {}
    result = encode_text(char, mapping=mapping)
    assert char in mapping
    assert len(result) == 2
    code = (result[0] << 8) | result[1]
    assert code == mapping[char]


def test_encode_text_reuses_existing_mapping():
    char = "𠮷"
    mapping = {char: 0xF040}
    result = encode_text(char, mapping=mapping)
    assert result == bytes([0xF0, 0x40])


def test_save_load_mapping_roundtrip(tmp_path):
    mapping = {"漢": 0xF040, "字": 0xF041}
    path = tmp_path / "map.json"
    save_mapping(path, mapping)
    loaded = load_mapping(path)
    assert loaded == mapping


def test_jis_private_codes_in_range():
    codes = list(jis_private_codes())
    assert codes[0] == 0xF040
    assert all(0xF040 <= c <= 0xF9FC for c in codes)
