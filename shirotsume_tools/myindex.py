import logging
from typing import List

import pandas as pd
from kola import Environment, KoiLang, kola_command, kola_env_enter, kola_text
from pydantic import validate_call

logger = logging.getLogger(__name__)


class MyIndex(KoiLang):
    __slots__ = ["raw_data", "data"]

    def at_start(self) -> None:
        self.raw_data = []
        self.data = None
        logger.debug("MyIndex started")

    def at_end(self) -> None:
        self.data = build_dataframe(self.raw_data)
        logger.debug("MyIndex finished, %d entries loaded", len(self.raw_data))

    class File(Environment):
        __slots__ = ["file_path", "info"]

        home: "MyIndex"

        @kola_env_enter
        def file(self, path: str) -> None:
            self.file_path = path
        
        @kola_command
        @validate_call
        def line(self, line: int, index: List[int]) -> None:
            self.info = (line, *index)
        
        @kola_text
        def text(self, text: str) -> str:
            self.home.raw_data.append((text, self.file_path, *self.info))
            return text
    
    def save_csv(self, path: str) -> None:
        assert self.data is not None, "data has not been loaded"
        logger.debug("Saving CSV to %s", path)
        self.data.to_csv(path, index=True)
    
    def save_excel(self, path: str) -> None:
        assert self.data is not None, "data has not been loaded"
        logger.debug("Saving Excel to %s", path)
        self.data.to_excel(path, index=True)


def build_dataframe(data: List[str]) -> pd.DataFrame:
    df = pd.DataFrame(data, columns=["raw_text"])
    return df.reindex(columns=["raw_text", "text", "comment"])
