import pytest
from shirotsume_tools.archive import PackEntry, write_pack, read_pack, replace_entries


def test_pack_roundtrip(tmp_path):
    header = b"\x00" * 16
    entries = [
        PackEntry(name="a.txt", data=b"hello world"),
        PackEntry(name="b.txt", data=b"second file"),
    ]
    pack_path = tmp_path / "test.dat"
    write_pack(pack_path, header, entries)
    read_header, read_entries = read_pack(pack_path)
    assert read_header == header
    assert len(read_entries) == 2
    assert read_entries[0].name == "a.txt"
    assert read_entries[0].data == b"hello world"
    assert read_entries[1].name == "b.txt"
    assert read_entries[1].data == b"second file"


def test_replace_entries(tmp_path):
    header = b"\x00" * 8
    entries = [PackEntry(name="script.txt", data=b"original")]
    src = tmp_path / "src.dat"
    write_pack(src, header, entries)
    out = tmp_path / "out.dat"
    replace_entries(src, out, {"script.txt": b"patched"})
    _, read_entries = read_pack(out)
    assert read_entries[0].data == b"patched"


def test_replace_entries_missing_key(tmp_path):
    header = b"\x00"
    entries = [PackEntry(name="a.txt", data=b"x")]
    src = tmp_path / "src.dat"
    write_pack(src, header, entries)
    out = tmp_path / "out.dat"
    with pytest.raises(KeyError):
        replace_entries(src, out, {"nonexistent.txt": b"y"})
