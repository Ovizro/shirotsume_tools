import pytest

from shirotsume_tools.archive import Archive, crypt, read_pack, replace_entries, write_pack
from shirotsume_tools.archive.crypt import PackEntry

# Bytes that decode only under MS932, not shift-jis.
# ① = U+2460, encoded as 0x87 0x40 in MS932.
NEC_CIRCLED_ONE = b"\x87\x40"


@pytest.fixture
def dat_path(tmp_path):
    """Synthetic RepiPack archive for compatibility/replace tests."""
    path = tmp_path / "sample.dat"
    header = b"\x00" * 16
    entries = [
        PackEntry("script.txt", b"original script content"),
        PackEntry("a.txt", b"hello world" * 1000),
        PackEntry("b.bin", bytes(range(256)) * 10),
        PackEntry("empty.txt", b""),
    ]
    with open(path, "wb") as f:
        crypt.pack(f, header, entries, compress=True)
    return path


def _pack_and_read(tmp_path, header, entries, compress):
    """Helper: pack entries and return the unpacker result."""
    out = tmp_path / "out.dat"
    with open(out, "wb") as f:
        crypt.pack(f, header, entries, compress=compress)

    with open(out, "rb") as f:
        unpacker = crypt.unpack(f)
        assert unpacker.header == header
        return list(unpacker)


def test_pack_unpack_roundtrip_compress_true(tmp_path):
    header = b"test header data"
    entries = [
        PackEntry("a.txt", b"hello world" * 1000),
        PackEntry("b.bin", bytes(range(256)) * 10),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert [e.name for e in result] == ["a.txt", "b.bin"]
    assert result[0].data == entries[0].data
    assert result[1].data == entries[1].data


def test_pack_unpack_roundtrip_compress_false(tmp_path):
    header = b"test header data"
    entries = [
        PackEntry("a.txt", b"hello world" * 1000),
        PackEntry("b.bin", bytes(range(256)) * 10),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=False)
    assert [e.name for e in result] == ["a.txt", "b.bin"]
    assert result[0].data == entries[0].data
    assert result[1].data == entries[1].data


def test_pack_unpack_empty_file_compress_true(tmp_path):
    header = b""
    entries = [PackEntry("empty.txt", b"")]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert len(result) == 1
    assert result[0].name == "empty.txt"
    assert result[0].data == b""


def test_pack_unpack_empty_file_compress_false(tmp_path):
    header = b""
    entries = [PackEntry("empty.txt", b"")]
    result = _pack_and_read(tmp_path, header, entries, compress=False)
    assert len(result) == 1
    assert result[0].name == "empty.txt"
    assert result[0].data == b""


def test_pack_unpack_binary_patterns(tmp_path):
    header = b"\x01\x02\x03\x04"
    entries = [
        PackEntry("zeros.bin", b"\x00" * 1024),
        PackEntry("ones.bin", b"\xff" * 1024),
        PackEntry("mixed.bin", b"\x00\xff" * 512),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert [e.name for e in result] == ["zeros.bin", "ones.bin", "mixed.bin"]
    for orig, got in zip(entries, result, strict=True):
        assert got.data == orig.data


def test_pack_unpack_repeated_patterns(tmp_path):
    """Repeated patterns exercise the LZSS compressor."""
    header = b"lzss"
    entries = [
        PackEntry("repeat.txt", b"abc" * 10000),
        PackEntry("run.bin", b"A" * 10000),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert result[0].data == b"abc" * 10000
    assert result[1].data == b"A" * 10000


def test_unpack_matches_archive_file_list(dat_path):
    """New crypt.unpack API returns the same names as the Archive wrapper."""
    with Archive(dat_path) as arc:
        old_list = arc.file_list

    with open(dat_path, "rb") as f:
        new_list = [e.name() for e in crypt.unpack(f).entries]

    assert new_list == old_list


def test_replace_entries_roundtrip(tmp_path, dat_path):
    out = tmp_path / "replaced.dat"
    replace_entries(dat_path, out, {"script.txt": b"replaced content"}, compress=True)

    _header, entries = read_pack(out)
    names = [e.name for e in entries]
    assert "script.txt" in names
    target = next(e for e in entries if e.name == "script.txt")
    assert target.data == b"replaced content"


def test_replace_entries_preserves_others(tmp_path, dat_path):
    out = tmp_path / "replaced.dat"
    replace_entries(dat_path, out, {"a.txt": b"new a"}, compress=True)

    _, entries = read_pack(out)
    names = [e.name for e in entries]
    assert "a.txt" in names
    assert "b.bin" in names
    assert "empty.txt" in names
    target = next(e for e in entries if e.name == "a.txt")
    assert target.data == b"new a"
    b_entry = next(e for e in entries if e.name == "b.bin")
    assert b_entry.data == bytes(range(256)) * 10
    empty_entry = next(e for e in entries if e.name == "empty.txt")
    assert empty_entry.data == b""


def test_replace_entries_missing_key(tmp_path, dat_path):
    out = tmp_path / "replaced.dat"
    with pytest.raises(KeyError):
        replace_entries(dat_path, out, {"nonexistent.txt": b"x"}, compress=True)


# ---------------------------------------------------------------------------
# MS932 vs shift-jis regression tests
#
# MS932 (cp932) is a superset of shift-jis: it includes NEC special characters
# in the 0x8740-0x875F range (①②③…⑳ etc.) that strict shift-jis cannot decode.
# The game data uses these characters extensively (e.g. in S/*.txt), so all
# decoding must use "MS932", never "shift-jis".
# ---------------------------------------------------------------------------


def test_nec_char_fails_shift_jis_but_decodes_ms932():
    """Guard: ensure the test bytes actually distinguish the two codecs."""
    with pytest.raises(UnicodeDecodeError):
        NEC_CIRCLED_ONE.decode("shift-jis")
    assert NEC_CIRCLED_ONE.decode("ms932") == "\u2460"  # ①


def test_ms932_filename_with_nec_char(tmp_path):
    """PackEntry names with NEC special chars must round-trip via cp932/ms932."""
    filename = "\u2460.txt"  # ①.txt
    header = b"\x00" * 8
    entries = [PackEntry(filename, b"hello")]
    pack_path = tmp_path / "nec.dat"
    write_pack(pack_path, header, entries, compress=False)

    _, read_entries = read_pack(pack_path)
    assert read_entries[0].name == filename


def test_ms932_content_with_nec_char(tmp_path):
    """Text-mode extraction must decode NEC special chars using MS932."""
    raw_content = "\u2460\u2461\u2462".encode("ms932")
    filename = "test.txt"
    header = b"\x00" * 8
    entries = [PackEntry(filename, raw_content)]
    pack_path = tmp_path / "nec_content.dat"
    write_pack(pack_path, header, entries, compress=False)

    outdir = tmp_path / "extracted"
    with Archive(pack_path) as arc:
        arc.extract_all(outdir, encoding="ms932")

    out = (outdir / filename).read_text(encoding="ms932")
    assert out == "\u2460\u2461\u2462"


def test_public_pack_entry_has_crypt_type():
    """shirotsume_tools.archive.PackEntry must preserve crypt_type for BC."""
    from shirotsume_tools.archive import PackEntry

    pe = PackEntry("a.txt", b"x", crypt_type=2)
    assert pe.crypt_type == 2


def test_replace_entries_callable(tmp_path, dat_path):
    """replace_entries accepts a callable that returns bytes or None."""
    out = tmp_path / "replaced.dat"

    def repl(name):
        if name == "script.txt":
            return b"replaced content"
        return None

    replace_entries(dat_path, out, repl, compress=True)

    _header, entries = read_pack(out)
    target = next(e for e in entries if e.name == "script.txt")
    assert target.data == b"replaced content"
    b_entry = next(e for e in entries if e.name == "b.bin")
    assert b_entry.data == bytes(range(256)) * 10


def test_roundtrip_header_size_zero(tmp_path):
    """A zero-byte header must round-trip without malloc(0)/memcpy UB."""
    header = b""
    entries = [
        PackEntry("a.txt", b"hello world" * 100),
        PackEntry("b.bin", bytes(range(256)) * 5),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert [e.name for e in result] == ["a.txt", "b.bin"]
    assert result[0].data == entries[0].data
    assert result[1].data == entries[1].data
