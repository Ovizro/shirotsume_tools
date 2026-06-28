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
    logger.info("Parsed %d statements, %d characters", index.statement_count, index.character_count)


from ..translation import patch_script_file, sync_translation_csvs, translate_scripts


def patch_script_cmd(
    script_path: Path = typer.Argument(help="Extracted script text file to patch"),
    replacements_path: Path = typer.Argument(help="CSV or JSON replacements"),
    out_path: Path = typer.Argument(help="Output patched script path"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of the extracted script"),
    mapping_path: Path | None = typer.Option(None, "-m", "--mapping", help="JSON custom character map to read/update"),
) -> None:
    """Patch dialogue strings in an extracted script and encode with custom JIS-compatible bytes."""
    count = patch_script_file(
        script_path,
        replacements_path,
        out_path,
        source_encoding=source_encoding,
        mapping_path=mapping_path,
    )
    logger.info("Patched %d text span(s) into %s", count, out_path)
    if mapping_path:
        logger.info("Updated custom encoding map: %s", mapping_path)


def translate_scripts_cmd(
    script_dir: Path = typer.Argument(help="Directory containing extracted game scripts, for example ./S"),
    replacements_dir: Path = typer.Option(
        Path("translation_patch/translations"),
        "-o",
        "--out",
        help="Directory for generated replacement CSV files",
    ),
    patched_dir: Path | None = typer.Option(
        Path("translation_patch/scripts/S"),
        "-p",
        "--patched-dir",
        help="Directory for patched script files, or omit with --no-patch",
    ),
    mapping_path: Path | None = typer.Option(
        Path("translation_patch/scripts/shiro_patch_charmap.json"),
        "-m",
        "--mapping",
        help="JSON custom character map to read/update while emitting patched scripts",
    ),
    memory_path: Path | None = typer.Option(
        Path("translation_patch/translation_memory.json"),
        "--memory",
        help="Persistent translation memory JSON file",
    ),
    model: str | None = typer.Option(None, "--model", help="OpenAI model, defaults to OPENAI_MODEL or gpt-4.1"),
    api_base_url: str | None = typer.Option(None, "--api-base-url", help="Custom OpenAI-compatible API base URL"),
    target_language: str = typer.Option("Simplified Chinese", "-t", "--target-language", help="Translation target language"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of extracted scripts"),
    batch_size: int = typer.Option(24, "-b", "--batch-size", min=1, help="Number of strings per OpenAI request"),
    max_source_chars: int = typer.Option(
        6000,
        "--max-source-chars",
        min=1,
        help="Maximum source characters per OpenAI request",
    ),
    limit: int | None = typer.Option(None, "--limit", min=1, help="Translate only the first N strings"),
    story_context: str = typer.Option("", "--context", help="Global story/style context passed to the translator"),
    temperature: float = typer.Option(0.2, "--temperature", min=0.0, max=2.0, help="OpenAI sampling temperature"),
    prompt_language: str = typer.Option("en", "--prompt-language", help="System prompt language: en or zh"),
    no_patch: bool = typer.Option(False, "--no-patch", help="Write replacement CSVs only"),
) -> None:
    """Translate extracted scripts to Chinese with OpenAI and optionally emit patched script files."""
    count = translate_scripts(
        script_dir,
        replacements_dir,
        patched_dir=None if no_patch else patched_dir,
        mapping_path=None if no_patch else mapping_path,
        model=model,
        api_base_url=api_base_url,
        target_language=target_language,
        source_encoding=source_encoding,
        batch_size=batch_size,
        max_source_chars=max_source_chars,
        limit=limit,
        story_context=story_context,
        temperature=temperature,
        memory_path=memory_path,
        prompt_language=prompt_language,
    )
    logger.info("Translated %d text span(s)", count)


def sync_translation_csvs_cmd(
    script_dir: Path = typer.Argument(help="Directory containing extracted game scripts, for example ./S"),
    replacements_dir: Path = typer.Option(
        Path("translation_patch/translations"),
        "-o",
        "--out",
        help="Directory containing replacement CSV files to preserve and extend",
    ),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of extracted scripts"),
) -> None:
    """Append newly detected text spans to replacement CSVs without calling the translation API."""
    added = sync_translation_csvs(script_dir, replacements_dir, source_encoding=source_encoding)
    logger.info("Added %d untranslated text span(s)", added)
