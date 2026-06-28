import importlib.util
from typing import TYPE_CHECKING

from ..index import Index

if TYPE_CHECKING:
    import pandas as pd


def _to_records(index: Index) -> list[dict]:
    return [
        {
            "raw_text": entry.text,
            "text": "",
            "comment": "",
            "file": entry.file_path,
            "line": entry.line,
            "start": entry.index[0] if entry.index else 0,
            "stop": entry.index[1] if len(entry.index) > 1 else 0,
        }
        for entry in index.entries
    ]


def to_dataframe(index: Index) -> "pd.DataFrame":
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "exporting to DataFrame requires 'pandas'. Install with: pip install shirotsume_tools[export]"
        ) from e
    return pd.DataFrame(_to_records(index))


def to_csv(index: Index, path: str, *, index_label: bool = True) -> None:
    df = to_dataframe(index)
    df.to_csv(path, index=index_label)


def to_excel(index: Index, path: str) -> None:
    if importlib.util.find_spec("openpyxl") is None:
        raise ImportError("exporting to Excel requires 'openpyxl'. Install with: pip install shirotsume_tools[export]")
    df = to_dataframe(index)
    df.to_excel(path, index=False)
