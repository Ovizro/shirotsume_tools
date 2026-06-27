from pydantic import BaseModel, ConfigDict


class FileEntry(BaseModel):
    """归档中的单个文件条目"""
    model_config = ConfigDict(frozen=True)

    name: str
    offset: int
    size: int
    comp_size: int
    crypt_type: int
