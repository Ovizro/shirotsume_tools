from pydantic import BaseModel, ConfigDict


class TextEntry(BaseModel):
    """从脚本中提取的单条文本条目"""

    model_config = ConfigDict(frozen=True)

    text: str
    file_path: str
    line: int
    start: int
    stop: int
