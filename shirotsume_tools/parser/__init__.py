import logging
import os
from glob import glob
from typing import List, Tuple, Union

from antlr4 import CommonTokenStream, FileStream
from antlr4.CommonTokenFactory import CommonToken
from kola.klvm.koilang import KoiLangWriter

from ..myindex import MyIndex
from .ShirotsumeLexer import ShirotsumeLexer
from .ShirotsumeListener import ShirotsumeListener
from .ShirotsumeParser import ShirotsumeParser

logger = logging.getLogger(__name__)


statement_counter = 0
character_counter = 0


class Listener(ShirotsumeListener):
    def __init__(self, writer: MyIndex):
        self.writer = writer
        self.texts = []

    def exitFunction_call(self, ctx: ShirotsumeParser.Function_callContext):
        global statement_counter, character_counter
        name = ctx.LITERAL()
        args = ctx.function_arguments()
        if name is None or args is None:
            return
        name = name.getText()  # type: ignore
        logger.debug("Function call: %s", name)
        exprs: List[ShirotsumeParser.ExpressionContext] = args.expression()
        if name == "CreateBalloon":
            text_token = exprs[-1].getToken(ShirotsumeLexer.STRING, 0)
        elif name == "CreateBalloonEx":
            text_token = exprs[-4].getToken(ShirotsumeLexer.STRING, 0)
        elif name == "AddText":
            text_token = exprs[1].getToken(ShirotsumeLexer.STRING, 0)
        else:
            return
        statement_counter += 1
        assert text_token is not None
        text_syn: CommonToken = text_token.getSymbol()
        text = text_syn.text
        assert text is not None and text.startswith('"') and text.endswith('"')
        text = text[1:-1].replace("\r", "")
        character_counter += len(text)
        self.texts.append(text)
        self.writer.File.line(text_syn.line, index=[text_syn.start, text_syn.stop])
        self.writer.File.text(text)
        self.writer.newline()

def parse_file(path: str, writer: Union[KoiLangWriter, str], *, encoding: str = "utf-8") -> List[str]:
    logger.info("Parsing file: %s (encoding=%s)", path, encoding)
    input_stream = FileStream(path, encoding=encoding)
    lexer = ShirotsumeLexer(input_stream)
    parser = ShirotsumeParser(CommonTokenStream(lexer))

    if isinstance(writer, str):
        shuold_close = True
        writer = MyIndex.writer(writer)
    else:
        shuold_close = False

    listener = Listener(writer)
    try:
        parser.addParseListener(listener)
        writer.File.file(path)
        writer.newline()
        parser.program()
    finally:
        if shuold_close:
            writer.__exit__()
    return listener.texts


def parse(path: str, writer: Union[KoiLangWriter, str], *, encoding: str = "utf-8") -> List[str]:
    logger.info("Parsing path: %s (encoding=%s)", path, encoding)
    if isinstance(writer, str):
        shuold_close = True
        writer = MyIndex.writer(writer)
    else:
        shuold_close = False
    texts = []
    try:
        if not os.path.isdir(path):
            return parse_file(path, writer, encoding=encoding)
        for file in glob(os.path.join(path, "**.txt"), recursive=True):
            if os.path.isdir(file):
                continue
            texts.extend(parse_file(file, writer, encoding=encoding))
    finally:
        if shuold_close:
            writer.__exit__()
    return texts


def reset_counter() -> None:
    global statement_counter, character_counter
    statement_counter = 0
    character_counter = 0


def get_counter() -> Tuple[int, int]:
    return statement_counter, character_counter
