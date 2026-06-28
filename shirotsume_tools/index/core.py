from pydantic import BaseModel, Field

from ..parser.model import TextEntry
from .model import IndexEntry


class Index(BaseModel):
    """文本条目集合"""

    entries: list[IndexEntry] = Field(default_factory=list)

    def add(self, entry: IndexEntry) -> None:
        self.entries.append(entry)

    def add_text(self, text: str, file_path: str, line: int, start: int, stop: int) -> None:
        self.entries.append(IndexEntry(text=text, file_path=file_path, line=line, index=(start, stop)))

    @classmethod
    def from_text_entries(cls, entries: list[TextEntry]) -> "Index":
        return cls(
            entries=[IndexEntry(text=e.text, file_path=e.file_path, line=e.line, index=(e.start, e.stop)) for e in entries]
        )

    @property
    def statement_count(self) -> int:
        return len(self.entries)

    @property
    def character_count(self) -> int:
        return sum(len(e.text) for e in self.entries)

    def save(self, path: str) -> None:
        from .io import write_index

        write_index(self, path)

    @classmethod
    def load(cls, path: str) -> "Index":
        from .io import read_index

        return read_index(path)
