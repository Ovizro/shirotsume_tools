from pydantic import BaseModel, ConfigDict


class IndexEntry(BaseModel):
    """索引中的单条记录"""

    model_config = ConfigDict(frozen=True)

    text: str
    file_path: str
    line: int
    index: tuple[int, ...]
