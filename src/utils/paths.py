
import sys
import os
from pathlib import Path

# When frozen by PyInstaller, sys.executable is the path to the exe.
# sys._MEIPASS is the temp folder where resources are unpacked.
# When running as script, use the current working directory or relative to this file.

def get_base_path() -> Path:
    """Returns the base path of the application (unpacked source or _MEIPASS)."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    
    # If not frozen, we assume we are in src/utils/paths.py
    # So base is 3 levels up: src/utils/ -> src/ -> APP_ROOT
    return Path(__file__).resolve().parent.parent.parent

def get_bin_dir() -> Path:
    return get_base_path() / "bin"

def get_templates_dir() -> Path:
    return get_base_path() / "templates"

def get_pandoc_exe() -> Path:
    exe_name = "pandoc.exe" if sys.platform == "win32" else "pandoc"
    # First check bundled bin
    bundled = get_bin_dir() / exe_name
    if bundled.exists():
        return bundled
    # Fallback to system path
    system_path = shutil.which("pandoc")
    if system_path:
        return Path(system_path)
    return bundled # Return bundled path even if missing, to avoid None crashes upstream, or handle there

def get_typst_exe() -> Path:
    exe_name = "typst.exe" if sys.platform == "win32" else "typst"
    bundled = get_bin_dir() / exe_name
    if bundled.exists():
        return bundled
    # Fallback to system path
    system_path = shutil.which("typst")
    if system_path:
        return Path(system_path)
    return bundled

def get_resource_path(relative_path: str) -> Path:
    """Helper to get a resource path relative to the base path."""
    return get_base_path() / relative_path

import shutil
