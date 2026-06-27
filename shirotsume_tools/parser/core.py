import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from glob import glob

from antlr4 import CommonTokenStream, FileStream

from .listener import TextExtractionListener
from .model import TextEntry


def parse_script(path: str, *, encoding: str = "utf-8") -> list[TextEntry]:
    input_stream = FileStream(path, encoding=encoding)
    from .ShirotsumeLexer import ShirotsumeLexer
    from .ShirotsumeParser import ShirotsumeParser
    lexer = ShirotsumeLexer(input_stream)
    parser = ShirotsumeParser(CommonTokenStream(lexer))
    listener = TextExtractionListener(path)
    parser.addParseListener(listener)
    parser.program()
    return listener.entries


def parse_directory(path: str, *, encoding: str = "utf-8",
                    max_workers: int | None = None) -> list[TextEntry]:
    files = [
        f for f in glob(os.path.join(path, "**", "*.txt"), recursive=True)
        if not os.path.isdir(f)
    ]
    if not files:
        return []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(
            partial(_parse_single, encoding=encoding), files
        ))
    entries = []
    for file_entries in results:
        entries.extend(file_entries)
    return entries


def _parse_single(path: str, *, encoding: str) -> list[TextEntry]:
    return parse_script(path, encoding=encoding)
