
import pytest
from unittest.mock import patch, mock_open
from src.utils.i18n import TranslationManager

def test_i18n_singleton():
    """Verify singleton behavior."""
    cls = TranslationManager
    # Reset for test
    cls._instance = None
    i1 = cls()
    i2 = cls()
    assert i1 is i2

def test_translation_defaults():
    """Test default fallback behavior."""
    cls = TranslationManager
    cls._instance = None 
    
    # Mock file loading to avoid FS dependency and ensure deterministic data
    with patch("builtins.open", mock_open(read_data='{"hello": "Ciao"}')) as m:
        tm = cls()
        # Force load called by init
        
        # Test translation
        # Since we mocked open, it reads "Ciao" for both IT and EN calls in init
        # But we can inject manual data
        tm.translations = {
            "it": {"hello": "Ciao", "only_it": "Solo IT"},
            "en": {"hello": "Hello"}
        }
        tm.current_locale = "en"
        
        assert tm.t("hello") == "Hello"
        # Test fallback to IT
        assert tm.t("only_it") == "Solo IT"
        # Test missing key keys
        assert tm.t("missing_key") == "missing_key"
        assert tm.t("missing_key", default="D") == "D"
