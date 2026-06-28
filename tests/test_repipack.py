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


def test_crypt_pack_entry_crypt_type_roundtrip(tmp_path):
    """crypt.PackEntry.crypt_type is written to the archive table."""
    header = b""
    entries = [PackEntry("a.txt", b"hello", crypt_type=1)]
    out = tmp_path / "out.dat"
    with open(out, "wb") as f:
        crypt.pack(f, header, entries)
    with open(out, "rb") as f:
        unpacker = crypt.unpack(f)
        assert unpacker.entries[0].crypt_type() == 1
        assert next(iter(unpacker)).data == b"hello"


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


# ---------------------------------------------------------------------------
# crypt_type=2 (file_encrypt_words) regression tests
#
# The game stores audio archives (K.dat, M.dat) with crypt_type=2, which uses
# a different cipher than the default crypt_type=1 (crypt_words).  The encoder
# originally only implemented crypt_type=1 and silently wrote type=1 data
# even when the source used type=2, producing archives that could not be
# decoded correctly by the game.
# ---------------------------------------------------------------------------


def test_crypt_type_2_roundtrip(tmp_path):
    """Entries with crypt_type=2 must round-trip through pack/unpack."""
    header = b"\x00" * 8
    entries = [
        PackEntry("a.wav", b"\x00" * 1024, crypt_type=2),
        PackEntry("b.wav", bytes(range(256)) * 8, crypt_type=2),
    ]
    result = _pack_and_read(tmp_path, header, entries, compress=False)
    assert [e.name for e in result] == ["a.wav", "b.wav"]
    assert result[0].data == entries[0].data
    assert result[1].data == entries[1].data
    # The archive must record crypt_type=2, not the default 1
    with open(tmp_path / "out.dat", "rb") as f:
        unpacker = crypt.unpack(f)
        assert unpacker.entries[0].crypt_type() == 2
        assert unpacker.entries[1].crypt_type() == 2


def test_crypt_type_2_differs_from_type_1():
    """crypt_type=2 must produce different ciphertext than type=1."""
    data = b"hello world" * 100
    enc1, ct1 = crypt.encode_body(data, compress=False, crypt_type_in=1)
    enc2, ct2 = crypt.encode_body(data, compress=False, crypt_type_in=2)
    assert ct1 == 1
    assert ct2 == 2
    assert enc1 != enc2
    # Both must decrypt back to the original
    assert crypt.decode_body(enc1, len(data), ct1) == data
    assert crypt.decode_body(enc2, len(data), ct2) == data


def test_unpacker_preserves_crypt_type(tmp_path):
    """Unpacker.__next__ must carry crypt_type into the yielded PackEntry."""
    header = b"\x00" * 4
    entries = [
        PackEntry("type1.bin", b"data for type 1", crypt_type=1),
        PackEntry("type2.bin", b"data for type 2", crypt_type=2),
    ]
    out = tmp_path / "mixed.dat"
    with open(out, "wb") as f:
        crypt.pack(f, header, entries, compress=False)

    with open(out, "rb") as f:
        unpacker = crypt.unpack(f)
        yielded = list(unpacker)

    assert yielded[0].crypt_type == 1
    assert yielded[1].crypt_type == 2


def test_reencode_uncompressed_crypt_type_2_byte_identical(tmp_path):
    """Decode-then-reencode of an uncompressed type-2 archive must be
    byte-identical, exercising file_encrypt_words as the inverse of
    file_decrypt_words."""
    header = b"\x00\x01\x02\x03"
    original_entries = [
        PackEntry(f"file{i}.bin", bytes((i * 7) % 256 for _ in range(2000)), crypt_type=2)
        for i in range(5)
    ]

    src = tmp_path / "src.dat"
    with open(src, "wb") as f:
        crypt.pack(f, header, original_entries, compress=False)

    # Read back and re-encode
    with open(src, "rb") as f:
        unpacker = crypt.unpack(f)
        read_header = unpacker.header
        read_entries = list(unpacker)
    assert read_header == header

    dst = tmp_path / "dst.dat"
    with open(dst, "wb") as f:
        crypt.pack(f, read_header, read_entries, compress=False)

    assert src.read_bytes() == dst.read_bytes()


def test_replace_preserves_crypt_type_of_untouched_entries(tmp_path):
    """replace_entries must keep the original crypt_type for entries
    that are merely copied, not replaced."""
    header = b"\x00" * 4
    entries = [
        PackEntry("keep.bin", b"keep me" * 100, crypt_type=2),
        PackEntry("replace.bin", b"old data" * 100, crypt_type=2),
    ]
    src = tmp_path / "src.dat"
    with open(src, "wb") as f:
        crypt.pack(f, header, entries, compress=False)

    out = tmp_path / "out.dat"
    replace_entries(src, out, {"replace.bin": b"new data" * 100}, compress=False)

    with open(out, "rb") as f:
        unpacker = crypt.unpack(f)
        assert unpacker.entries[0].crypt_type() == 2
        assert unpacker.entries[1].crypt_type() == 2


# ---------------------------------------------------------------------------
# LZSS self-referential match regression tests
#
# The compressor previously allowed matches whose window [off, off+len)
# overlapped the write window [cache_ptr, cache_ptr+len).  In that case
# the compressor wrote bytes from the match area (being modified during the
# write) while the decompressor read different, already-overwritten values,
# producing corrupted output.  The classic trigger is text with short
# repeating tokens (e.g. "233, ") whose period aligns with the cache
# pointer after the 0x1000-byte ring wraps.
# ---------------------------------------------------------------------------


def test_lzss_repeating_pattern_longer_than_cache(tmp_path):
    """Data with a short repeating period longer than the 0x1000-byte
    cache must round-trip without self-referential corruption."""
    pattern = b"233, "
    data = pattern * 5000  # 25000 bytes, well beyond the 4096-byte cache
    header = b"lzss"
    entries = [PackEntry("repeat.txt", data)]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert result[0].data == data


def test_lzss_short_period_repetition(tmp_path):
    """A 3-byte repeating pattern fills the ring buffer and wraps around,
    which can trigger self-referential matches at the wrap boundary."""
    data = b"abc" * 8192  # 24576 bytes, 6 full cache rotations
    header = b""
    entries = [PackEntry("abc.bin", data)]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert result[0].data == data


def test_lzss_quasi_periodic_text(tmp_path):
    """Quasi-periodic text (like game scripts with repeated dialogue
    markers) exercises self-referential match paths in the compressor."""
    # Full-width space (U+3000) encodes to 0x81 0x41 in cp932
    spacer = "\u3000".encode("cp932") * 20
    line = spacer + b"233, 233, 233, I10, 233, 233, 233, 233,\n"
    data = line * 1000
    header = b"script"
    entries = [PackEntry("10-01.txt", data)]
    result = _pack_and_read(tmp_path, header, entries, compress=True)
    assert result[0].data == data
