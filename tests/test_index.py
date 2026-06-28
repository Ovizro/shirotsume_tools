from shirotsume_tools.index import Index, IndexEntry
from shirotsume_tools.parser.model import TextEntry


def test_index_from_text_entries():
    entries = [
        TextEntry(text="hello", file_path="a.txt", line=1, start=10, stop=15),
        TextEntry(text="world", file_path="a.txt", line=2, start=20, stop=25),
    ]
    index = Index.from_text_entries(entries)
    assert index.statement_count == 2
    assert index.character_count == 10
    assert index.entries[0].index == (10, 15)


def test_index_save_load_roundtrip(tmp_path):
    index = Index()
    index.add(IndexEntry(text="你好", file_path="scene.txt", line=3, index=(5, 7)))
    path = tmp_path / "out.myi"
    index.save(str(path))
    loaded = Index.load(str(path))
    assert loaded.entries == index.entries
