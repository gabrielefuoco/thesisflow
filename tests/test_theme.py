
import pytest
from unittest.mock import Mock
from src.ui.theme import Theme

def test_theme_constants():
    """Verify key theme constants are present."""
    assert Theme.COLOR_BG.startswith("#")
    assert Theme.COLOR_ACCENT
    assert "Segoe" in Theme.FONT_FAMILY or "Arial" in Theme.FONT_FAMILY

def test_apply_to_panel():
    """Test applying theme to a panel widget."""
    mock_widget = Mock()
    Theme.apply_to(mock_widget, type="panel")
    mock_widget.configure.assert_called_with(fg_color=Theme.COLOR_PANEL)

def test_apply_to_main():
    """Test applying theme to main background."""
    mock_widget = Mock()
    Theme.apply_to(mock_widget, type="main")
    mock_widget.configure.assert_called_with(fg_color=Theme.COLOR_BG)
