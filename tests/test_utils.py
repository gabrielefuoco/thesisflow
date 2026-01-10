
import pytest
from src.utils.paths import get_base_path, get_pandoc_exe, get_typst_exe
from src.utils.logger import get_logger

def test_paths_sanity():
    """Verify paths return Path objects and typical structure."""
    base = get_base_path()
    assert base.exists()
    
    # We can't guarantee binaries exist in all envs (unless validated), 
    # but we check the return type
    assert str(get_pandoc_exe()).endswith("pandoc.exe") or str(get_pandoc_exe()).endswith("pandoc") 

def test_logger_singleton():
    """Verify that get_logger returns the same logger instance."""
    l1 = get_logger()
    l2 = get_logger()
    assert l1 is l2
    assert l1.name == "ThesisFlow"
