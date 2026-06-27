import glob
import logging
import os
from pathlib import Path
from shutil import rmtree
from typing import Optional

import typer

from . import decrypt, MyIndex, parse, get_counter, build_dataframe, patch_script_file
from .translate_agent import sync_translation_csvs
from .translate_agent import translate_scripts

logger = logging.getLogger(__name__)

app = typer.Typer(name="shirotsume_tools", help="tools for shirotsume")


@app.command("decrypt")
def decrypt_cmd(
    dat_file: str = typer.Argument(help="Path to .dat file, supports glob patterns"),
    outdir: Optional[Path] = typer.Option(None, "-o", "--outdir", help="Output directory"),
    encoding: Optional[str] = typer.Option(None, "-e", "--encoding", help="File encoding"),
    remove_old: bool = typer.Option(False, "-r", "--remove-old", help="Remove existing output directory"),
) -> None:
    """Decrypt .dat archive files."""
    if '*' in dat_file:
        outdir = outdir or Path('.')
        files = glob.glob(dat_file, recursive=True)
        logger.info("Glob pattern matched %d file(s)", len(files))
        for file in files:
            out = outdir / os.path.basename(file).split(".")[0]
            if remove_old:
                logger.debug("Removing existing directory %s", out)
                rmtree(out, ignore_errors=True)
            logger.info("Decrypting %s to %s", file, out)
            decrypt(file, out, encoding=encoding)
        return
    elif not dat_file.endswith(".dat"):
        logger.error("dat_file must be .dat file, got: %s", dat_file)
        raise typer.Exit(code=1)
    else:
        outdir = outdir or Path(os.path.basename(dat_file).split(".")[0])
        if remove_old:
            logger.debug("Removing existing directory %s", outdir)
            rmtree(outdir, ignore_errors=True)
        logger.info("Decrypting %s to %s", dat_file, outdir)
        decrypt(dat_file, outdir, encoding=encoding)
    logger.info("Done")


@app.command()
def myindex(
    myi_path: Path = typer.Argument(help="Path to .myi index file"),
    decode: Optional[str] = typer.Option(None, "-d", "--decode", help="Decode script name"),
    encoding: str = typer.Option("utf-8", "-e", "--encoding", help="File encoding"),
    out_csv: Optional[Path] = typer.Option(None, "-c", "--out-csv", help="Output CSV path"),
    out_excel: Optional[Path] = typer.Option(None, "-x", "--out-excel", help="Output Excel path"),
) -> None:
    """Parse and convert .myi index files."""
    if decode:
        logger.info("Parsing %s with decode=%s, encoding=%s", myi_path, decode, encoding)
        data = parse(decode, str(myi_path), encoding=encoding)
        statement, total = get_counter()
        logger.info("Parsed %d statements, %d total characters", statement, total)
        if out_csv or out_excel:
            logger.debug("Building dataframe from %d entries", len(data))
            df = build_dataframe(data)
            if out_csv:
                logger.info("Saving CSV to %s", out_csv)
                df.to_csv(out_csv, index=True)
            if out_excel:
                logger.info("Saving Excel to %s", out_excel)
                df.to_excel(out_excel, index=True)
        return
    logger.info("Loading myi file %s", myi_path)
    myi = MyIndex()
    myi.parse_file(myi_path, encoding="utf-8")
    if out_csv:
        logger.info("Saving CSV to %s", out_csv)
        myi.save_csv(out_csv)
    if out_excel:
        logger.info("Saving Excel to %s", out_excel)
        myi.save_excel(out_excel)
    logger.info("Done")


@app.command("patch-script")
def patch_script_cmd(
    script_path: Path = typer.Argument(help="Extracted script text file to patch"),
    replacements_path: Path = typer.Argument(help="CSV or JSON replacements"),
    out_path: Path = typer.Argument(help="Output patched script path"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of the extracted script"),
    mapping_path: Optional[Path] = typer.Option(None, "-m", "--mapping", help="JSON custom character map to read/update"),
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


@app.command("translate-scripts")
def translate_scripts_cmd(
    script_dir: Path = typer.Argument(help="Directory containing extracted game scripts, for example ./S"),
    replacements_dir: Path = typer.Option(
        Path("translation_patch/translations"),
        "-o",
        "--out",
        help="Directory for generated replacement CSV files",
    ),
    patched_dir: Optional[Path] = typer.Option(
        Path("translation_patch/scripts/S"),
        "-p",
        "--patched-dir",
        help="Directory for patched script files, or omit with --no-patch",
    ),
    mapping_path: Optional[Path] = typer.Option(
        Path("translation_patch/scripts/shiro_patch_charmap.json"),
        "-m",
        "--mapping",
        help="JSON custom character map to read/update while emitting patched scripts",
    ),
    memory_path: Optional[Path] = typer.Option(
        Path("translation_patch/translation_memory.json"),
        "--memory",
        help="Persistent translation memory JSON file",
    ),
    model: Optional[str] = typer.Option(None, "--model", help="OpenAI model, defaults to OPENAI_MODEL or gpt-4.1"),
    api_base_url: Optional[str] = typer.Option(None, "--api-base-url", help="Custom OpenAI-compatible API base URL"),
    target_language: str = typer.Option("Simplified Chinese", "-t", "--target-language", help="Translation target language"),
    source_encoding: str = typer.Option("cp932", "-e", "--source-encoding", help="Encoding of extracted scripts"),
    batch_size: int = typer.Option(24, "-b", "--batch-size", min=1, help="Number of strings per OpenAI request"),
    max_source_chars: int = typer.Option(6000, "--max-source-chars", min=1, help="Maximum source characters per OpenAI request"),
    limit: Optional[int] = typer.Option(None, "--limit", min=1, help="Translate only the first N strings"),
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


@app.command("sync-translation-csvs")
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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable verbose logging"),
) -> None:
    """tools for shirotsume"""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


if __name__ == "__main__":
    app()
