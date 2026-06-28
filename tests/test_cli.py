from typer.testing import CliRunner

from shirotsume_tools.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "shirotsume_tools" in result.output


def test_parse_command(tmp_path):
    script = tmp_path / "test.txt"
    script.write_text('CreateBalloon("x", "hello");', encoding="utf-8")
    out = tmp_path / "out.myi"
    result = runner.invoke(app, ["parse", str(script), "--out-index", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_myindex_command(tmp_path):
    from shirotsume_tools.index import Index, IndexEntry

    index = Index()
    index.add(IndexEntry(text="hello", file_path="a.txt", line=1, index=(0, 5)))
    myi_path = tmp_path / "test.myi"
    index.save(str(myi_path))
    csv_path = tmp_path / "out.csv"
    result = runner.invoke(app, ["myindex", str(myi_path), "--out-csv", str(csv_path)])
    assert result.exit_code == 0
    assert csv_path.exists()
    assert "hello" in csv_path.read_text(encoding="utf-8")


def test_cli_help_includes_translation_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "patch-script" in result.output
    assert "translate-scripts" in result.output
    assert "sync-translation-csvs" in result.output


def test_sync_translation_csvs_command(tmp_path):
    script = tmp_path / "1-01.txt"
    script.write_text('page T {\nCreateBalloon("x", "テスト");\n}', encoding="cp932")
    repl_dir = tmp_path / "translations"
    result = runner.invoke(
        app,
        [
            "sync-translation-csvs",
            str(tmp_path),
            "-o",
            str(repl_dir),
            "-e",
            "cp932",
        ],
    )
    assert result.exit_code == 0
    assert (repl_dir / "1-01.csv").exists()
