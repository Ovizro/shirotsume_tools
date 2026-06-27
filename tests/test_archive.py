import pytest

from shirotsume_tools.archive import Archive, ArchiveError, InvalidSignatureError
from shirotsume_tools.archive.model import FileEntry


def test_archive_raises_on_missing_file(tmp_path):
    missing = tmp_path / "missing.dat"
    with pytest.raises(FileNotFoundError), Archive(missing):
        pass


def test_archive_context_manager_closes_file(tmp_path):
    dummy = tmp_path / "dummy.dat"
    dummy.write_bytes(b"not a real archive")
    with pytest.raises(ArchiveError), Archive(dummy) as arc:
        _ = arc.file_count


def test_archive_raises_invalid_signature(tmp_path):
    dummy = tmp_path / "bad.dat"
    dummy.write_bytes(b"NOTPACK" + b"\x00" * 100)
    with pytest.raises(InvalidSignatureError), Archive(dummy):
        pass


def test_file_entry_model():
    entry = FileEntry(name="test.txt", offset=0, size=100, comp_size=50, crypt_type=1)
    assert entry.name == "test.txt"
    assert entry.size == 100
