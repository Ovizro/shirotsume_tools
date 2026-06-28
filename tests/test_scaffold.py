def test_version():
    from shirotsume_tools import __version__
    assert __version__ == "0.2.1"


def test_submodules_importable():
    from shirotsume_tools import archive, cli, export, index, parser, translation  # noqa: F401
