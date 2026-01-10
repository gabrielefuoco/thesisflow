
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.engine.pandoc_wrapper import PandocWrapper
from src.engine.typst_wrapper import TypstWrapper

@pytest.fixture
def mock_pandoc_exe(mocker):
    """Mocks get_pandoc_exe to return a dummy path that 'exists'."""
    m = mocker.patch("src.engine.pandoc_wrapper.get_pandoc_exe")
    mock_path = Mock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.__str__ = Mock(return_value="/mock/pandoc")
    m.return_value = mock_path
    return mock_path

@pytest.fixture
def mock_typst_exe(mocker):
    """Mocks get_typst_exe."""
    m = mocker.patch("src.engine.typst_wrapper.get_typst_exe")
    mock_path = Mock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.__str__ = Mock(return_value="/mock/typst")
    m.return_value = mock_path
    return mock_path

def test_pandoc_wrapper_init_error(mocker):
    """Test error when executable not found."""
    m = mocker.patch("src.engine.pandoc_wrapper.get_pandoc_exe")
    m.return_value.exists.return_value = False
    with pytest.raises(FileNotFoundError):
        PandocWrapper()

def test_pandoc_conversion_command(mock_pandoc_exe, mocker):
    """Test that correct command is built and executed."""
    wrapper = PandocWrapper()
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    
    wrapper.convert_markdown_to_typst("MD Content", Path("out.typ"))
    
    # Check command structure
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert cmd[0] == "/mock/pandoc"
    assert "--from" in cmd and "markdown+tex_math_dollars" in cmd
    assert "--to" in cmd and "typst" in cmd
    assert "MD Content" == kwargs["input"]

def test_typst_wrapper_compile(mock_typst_exe, mocker):
    """Test typst compile command."""
    wrapper = TypstWrapper()
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    
    wrapper.compile(Path("in.typ"), Path("out.pdf"))
    
    args, _ = mock_run.call_args
    cmd = args[0]
    assert cmd[0] == "/mock/typst"
    assert "compile" in cmd
    assert "in.typ" in str(cmd)
    assert "out.pdf" in str(cmd)
