from antlr4.Token import CommonToken

from .model import TextEntry
from .ShirotsumeLexer import ShirotsumeLexer
from .ShirotsumeListener import ShirotsumeListener
from .ShirotsumeParser import ShirotsumeParser

TEXT_EXTRACTORS = {
    "CreateBalloon": lambda exprs: exprs[-1],
    "CreateBalloonEx": lambda exprs: exprs[-4],
    "CreateBalloonBie": lambda exprs: exprs[-1],
    "CreateText": lambda exprs: exprs[-1],
    "AddText": lambda exprs: exprs[1],
}


class TextExtractionListener(ShirotsumeListener):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entries: list[TextEntry] = []
        self.statement_count = 0
        self.character_count = 0

    def exitFunction_call(self, ctx: ShirotsumeParser.Function_callContext):
        name_token = ctx.LITERAL()
        args = ctx.function_arguments()
        if name_token is None or args is None:
            return
        name = name_token.getText()  # type: ignore[reportAttributeAccessIssue]
        extractor = TEXT_EXTRACTORS.get(name)
        if extractor is None:
            return
        exprs = args.expression()
        target_expr = extractor(exprs)
        text_token = target_expr.getToken(ShirotsumeLexer.STRING, 0)
        if text_token is None:
            return
        text_sym: CommonToken = text_token.getSymbol()
        raw = text_sym.text
        if not (raw and raw.startswith('"') and raw.endswith('"')):
            return
        text = raw[1:-1].replace("\r", "")
        self.entries.append(
            TextEntry(
                text=text,
                file_path=self.file_path,
                line=text_sym.line,
                start=text_sym.start,
                stop=text_sym.stop,
            )
        )
        self.statement_count += 1
        self.character_count += len(text)
