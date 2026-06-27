import io
import struct

import pytest


def test_decrypt_import():
    from shirotsume_tools.archive._decrypt import DecryptError, Decryptor, decrypt
    assert Decryptor is not None
    assert callable(decrypt)
    assert issubclass(DecryptError, Exception)


def test_decryptor_has_headers():
    from shirotsume_tools.archive._decrypt import Decryptor
    d = Decryptor()
    assert hasattr(d, "headers")


def test_module_name():
    from shirotsume_tools.archive._decrypt import Decryptor
    assert Decryptor.__module__ == "shirotsume_tools.archive._decrypt"


# ---------------------------------------------------------------------------
# MS932 vs shift-jis regression tests
#
# MS932 (cp932) is a superset of shift-jis: it includes NEC special characters
# in the 0x8740-0x875F range (①②③…⑳ etc.) that strict shift-jis cannot decode.
# The game data uses these characters extensively (e.g. in S/*.txt), so all
# decoding must use "MS932", never "shift-jis".
# ---------------------------------------------------------------------------

# Bytes that decode only under MS932, not shift-jis.
# ① = U+2460, encoded as 0x87 0x40 in MS932.
NEC_CIRCLED_ONE = b"\x87\x40"


def test_nec_char_fails_shift_jis_but_decodes_ms932():
    """Guard: ensure the test bytes actually distinguish the two codecs."""
    with pytest.raises(UnicodeDecodeError):
        NEC_CIRCLED_ONE.decode("shift-jis")
    assert NEC_CIRCLED_ONE.decode("ms932") == "\u2460"  # ①


def _encrypt(data: bytes, key: int) -> bytes:
    """Encrypt *data* using the RepiPack stream cipher.

    The decrypt function XORs each uint32 word with an evolving key where the
    key update uses the **plaintext**.  Encryption is therefore the inverse:
    XOR the plaintext to produce ciphertext, then update the key with the
    plaintext.
    """
    # Pad to 4-byte boundary (decrypt operates on uint32 words).
    pad = (-len(data)) % 4
    padded = data + b"\x00" * pad
    count = len(padded) // 4
    words = list(struct.unpack(f"<{count}I", padded))
    out = []
    for txt in words:
        out.append(txt ^ key)
        key = (key + (((txt << 16) | (txt >> 16)) ^ 0x98fcdba2)) & 0xFFFFFFFF
    return struct.pack(f"<{count}I", *out)[:len(data)]


def _build_archive(filename: str, content: bytes) -> bytes:
    """Build a minimal single-file RepiPack v2 archive."""
    name_bytes = filename.encode("ms932")
    assert len(name_bytes) < 0x40
    name_field = name_bytes + b"\x00" * (0x40 - len(name_bytes))

    # Layout: sig(8) + ver(4) + hdr_size(4) + hdr(4) + count(4) + fhdr(80) + data
    data_offset = 8 + 4 + 4 + 4 + 4 + 80

    file_header = bytearray(80)
    file_header[:0x40] = name_field
    struct.pack_into("<I", file_header, 0x40, data_offset)       # offset
    struct.pack_into("<I", file_header, 0x44, len(content))       # size
    struct.pack_into("<I", file_header, 0x48, len(content))       # comp_size
    file_header[0x4C] = 0                                          # crypt_type: none

    encrypted_fhdr = _encrypt(bytes(file_header), 0xF517AA26)
    encrypted_ahdr = _encrypt(b"\x00\x00\x00\x00", 0x837FC07A)

    return (
        b"RepiPack"
        + struct.pack("<I", 2)          # version
        + struct.pack("<I", 4)          # header_size
        + encrypted_ahdr               # header (4 bytes)
        + struct.pack("<I", 1)         # file_count
        + encrypted_fhdr               # file header (80 bytes)
        + content                      # file data
    )


def test_ms932_filename_with_nec_char(tmp_path):
    """file_list must decode NEC special chars (①) using MS932, not shift-jis."""
    from shirotsume_tools.archive._decrypt import Decryptor

    filename = "\u2460.txt"  # ①.txt
    content = b"hello"
    archive = _build_archive(filename, content)

    d = Decryptor()
    d.load(io.BytesIO(archive))
    assert d.file_list == ["\u2460.txt"]


def test_ms932_content_with_nec_char(tmp_path):
    """Text-mode extraction must decode NEC special chars using MS932."""
    from shirotsume_tools.archive._decrypt import Decryptor

    # Content: ①②③ encoded in MS932
    raw_content = "\u2460\u2461\u2462".encode("ms932")
    filename = "test.txt"
    archive = _build_archive(filename, raw_content)

    d = Decryptor()
    f = io.BytesIO(archive)
    d.load(f)
    d.dump_file(f, 0, str(tmp_path), encoding="ms932")

    # File is written in text mode with encoding="ms932", so reading back
    # with MS932 should reconstruct the original Unicode string.
    out = (tmp_path / "test.txt").read_text(encoding="ms932")
    assert out == "\u2460\u2461\u2462"
