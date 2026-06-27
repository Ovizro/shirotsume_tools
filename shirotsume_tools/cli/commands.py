import glob
import logging
import os
from pathlib import Path
from shutil import rmtree

import typer

from ..archive import decrypt
from ..export import to_csv, to_excel
from ..index import Index
from ..parser import parse_directory, parse_script

logger = logging.getLogger(__name__)


def decrypt_cmd(
    dat_file: str = typer.Argument(help="Path to .dat file, supports glob patterns"),
    outdir: Path | None = typer.Option(None, "-o", "--outdir"),
    encoding: str | None = typer.Option(None, "-e", "--encoding"),
    remove_old: bool = typer.Option(False, "-r", "--remove-old"),
) -> None:
    outdir = outdir or Path(".")
    files = glob.glob(dat_file, recursive=True) if "*" in dat_file else [dat_file]
    for file in files:
        if not file.endswith(".dat"):
            logger.error("skipping non-.dat file: %s", file)
            continue
        out = outdir / os.path.basename(file).split(".")[0]
        if remove_old:
            rmtree(out, ignore_errors=True)
        logger.info("Decrypting %s to %s", file, out)
        decrypt(file, out, encoding=encoding)
    logger.info("Done")


def myindex(
    myi_path: Path = typer.Argument(help="Path to .myi/.ktxt index file"),
    out_csv: Path | None = typer.Option(None, "-c", "--out-csv"),
    out_excel: Path | None = typer.Option(None, "-x", "--out-excel"),
) -> None:
    logger.info("Loading index file %s", myi_path)
    index = Index.load(str(myi_path))
    if out_csv:
        to_csv(index, str(out_csv))
    if out_excel:
        to_excel(index, str(out_excel))
    logger.info("Done")


def parse_cmd(
    script_path: Path = typer.Argument(help="Path to script file or directory"),
    out_index: Path | None = typer.Option(None, "-i", "--out-index"),
    out_csv: Path | None = typer.Option(None, "-c", "--out-csv"),
    encoding: str = typer.Option("utf-8", "-e", "--encoding"),
) -> None:
    if script_path.is_dir():
        entries = parse_directory(str(script_path), encoding=encoding)
    else:
        entries = parse_script(str(script_path), encoding=encoding)
    index = Index.from_text_entries(entries)
    if out_index:
        index.save(str(out_index))
    if out_csv:
        to_csv(index, str(out_csv))
    logger.info("Parsed %d statements, %d characters",
                index.statement_count, index.character_count)
