import typer

from .commands import (
    decrypt_cmd,
    myindex,
    parse_cmd,
    patch_script_cmd,
    sync_translation_csvs_cmd,
    translate_scripts_cmd,
)
from .logging_config import configure_logging

app = typer.Typer(name="shirotsume_tools", help="tools for shirotsume")

app.command("decrypt")(decrypt_cmd)
app.command("myindex")(myindex)
app.command("parse")(parse_cmd)
app.command("patch-script")(patch_script_cmd)
app.command("translate-scripts")(translate_scripts_cmd)
app.command("sync-translation-csvs")(sync_translation_csvs_cmd)
app.callback(invoke_without_command=True)(configure_logging)

if __name__ == "__main__":
    app()
