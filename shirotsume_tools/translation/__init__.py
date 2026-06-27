from .agent import extract_translation_items, sync_translation_csvs, translate_scripts
from .encoding import encode_script_text, encode_text, load_mapping, save_mapping
from .errors import TranslationError
from .patch import load_replacements, normalize_replacement_text, patch_dat_script, patch_script_file, patch_script_text

__all__ = [
    "TranslationError",
    "encode_script_text",
    "encode_text",
    "extract_translation_items",
    "load_mapping",
    "load_replacements",
    "normalize_replacement_text",
    "patch_dat_script",
    "patch_script_file",
    "patch_script_text",
    "save_mapping",
    "sync_translation_csvs",
    "translate_scripts",
]
