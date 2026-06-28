import pandas as pd

from shirotsume_tools.export import to_csv, to_dataframe, to_excel
from shirotsume_tools.index import Index, IndexEntry


def test_to_dataframe():
    index = Index()
    index.add(IndexEntry(text="hello", file_path="a.txt", line=1, index=(0, 5)))
    df = to_dataframe(index)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["raw_text"] == "hello"
    assert df.iloc[0]["start"] == 0
    assert df.iloc[0]["stop"] == 5


def test_to_csv(tmp_path):
    index = Index()
    index.add(IndexEntry(text="hello", file_path="a.txt", line=1, index=(0, 5)))
    path = tmp_path / "out.csv"
    to_csv(index, str(path))
    content = path.read_text(encoding="utf-8")
    assert "hello" in content


def test_to_excel(tmp_path):
    from shirotsume_tools.index import Index, IndexEntry

    index = Index()
    index.add(IndexEntry(text="hello", file_path="a.txt", line=1, index=(0, 5)))
    path = tmp_path / "out.xlsx"
    to_excel(index, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
