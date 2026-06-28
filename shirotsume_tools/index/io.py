from collections.abc import Iterable
from itertools import groupby

from koilang import Runtime, Writer

from .core import Index
from .model import IndexEntry


class IndexReader:
    def __init__(self):
        self.index = Index()
        self._current_file = ""
        self._current_line = 0
        self._current_index = (0, 0)

    def do_file(self, path: str) -> None:
        self._current_file = path

    def do_line(self, line: int, index: Iterable[int] = ()) -> None:
        self._current_line = line
        self._current_index = tuple(index)

    def at_text(self, text: str) -> None:
        self.index.add(
            IndexEntry(
                text=text,
                file_path=self._current_file,
                line=self._current_line,
                index=self._current_index,
            )
        )


def read_index(path: str) -> Index:
    reader = IndexReader()
    runtime = Runtime()
    runtime.env_enter(reader)
    try:
        runtime.execute(path)
    finally:
        runtime.env_exit(reader)
    return reader.index


def write_index(index: Index, path: str) -> None:
    with Writer(path) as writer:
        for file_path, group in groupby(index.entries, key=lambda e: e.file_path):
            writer.do_file(file_path)
            writer.newline()
            with writer.indent():
                for entry in group:
                    writer.do_line(entry.line, index=list(entry.index))
                    writer.at_text(entry.text)
                    writer.newline()
