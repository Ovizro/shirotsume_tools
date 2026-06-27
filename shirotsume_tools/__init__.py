from .parser import parse_file, parse, get_counter, reset_counter
from .myindex import MyIndex, build_dataframe
from .script_patch import patch_script_file

try:
    from .decrypt import Decryptor, decrypt
except ModuleNotFoundError:
    Decryptor = None

    def decrypt(*args, **kwargs):
        raise RuntimeError("shirotsume_tools.decrypt extension is not available")


__all__ = [
    "parse_file",
    "parse",
    "get_counter",
    "reset_counter",
    "MyIndex",
    "Decryptor",
    "decrypt",
    "patch_script_file",
]
