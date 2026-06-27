import typer

from .commands import decrypt_cmd, myindex, parse_cmd
from .logging_config import configure_logging

app = typer.Typer(name="shirotsume_tools", help="tools for shirotsume")

app.command("decrypt")(decrypt_cmd)
app.command("myindex")(myindex)
app.command("parse")(parse_cmd)
app.callback(invoke_without_command=True)(configure_logging)

if __name__ == "__main__":
    app()
