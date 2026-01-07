
import sys
from pathlib import Path

# When frozen by PyInstaller, sys.executable is the path to the exe.
# sys._MEIPASS is the temp folder where resources are unpacked.
# When running as script, use the current working directory or relative to this file.

def get_base_path() -> Path:
    """Returns the base path of the application (unpacked source or _MEIPASS)."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    # If running from src/utils/paths.py, base is two levels up?
    # Actually, let's assume the CWD is the project root in dev mode for simplicity,
    # or derive it from this file's location.
    # This file is in src/utils/
    return Path(__file__).parent.parent.parent

def get_bin_dir() -> Path:
    return get_base_path() / "bin"

def get_templates_dir() -> Path:
    return get_base_path() / "templates"

def get_pandoc_exe() -> Path:
    ext = ".exe" if sys.platform == "win32" else ""
    return get_bin_dir() / f"pandoc{ext}"

def get_typst_exe() -> Path:
    ext = ".exe" if sys.platform == "win32" else ""
    return get_bin_dir() / f"typst{ext}"
