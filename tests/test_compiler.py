
import pytest
from pathlib import Path
from src.engine.compiler import CompilerEngine, CompilationError
from src.utils.paths import get_pandoc_exe, get_typst_exe

@pytest.fixture
def integration_compiler(project_manager):
    """Creates a CompilerEngine instance for integration testing."""
    pm = project_manager
    pm.create_project("Integration Test", "Me")
    return CompilerEngine(pm.current_project_path, pm.manifest)

@pytest.mark.skipif(not get_pandoc_exe().exists(), reason="Pandoc not found")
@pytest.mark.skipif(not get_typst_exe().exists(), reason="Typst not found")
def test_compile_real_pdf(integration_compiler):
    """Test the full compile flow with REAL Pandoc/Typst to PDF."""
    
    # 1. Create content
    c1 = integration_compiler.manifest.chapters[0]
    (integration_compiler.chapters_dir / c1.filename).write_text("# Intro\nThis is a real test.", encoding="utf-8")
    
    # 2. Compile
    integration_compiler.compile("pdf")
    
    # 3. Verify Output
    assert integration_compiler.output_pdf.exists()
    assert integration_compiler.output_pdf.stat().st_size > 0

def test_resolve_includes(integration_compiler):
    """Test recursive include resolution."""
    base_path = integration_compiler.chapters_dir
    (base_path / "main.md").write_text("See {{ include: sub.md }}", encoding="utf-8")
    (base_path / "sub.md").write_text("details", encoding="utf-8")
    result = integration_compiler._resolve_includes("See {{ include: sub.md }}", base_path)
    assert "See details" in result

def test_concatenate_chapters(integration_compiler):
    """Test concatenating multiple chapters."""
    c1 = integration_compiler.manifest.chapters[0]
    (integration_compiler.chapters_dir / c1.filename).write_text("Content 1", encoding="utf-8")
    # Add another chapter manually
    from src.engine.models import Chapter
    c2 = Chapter(id="c2", title="C2", filename="c2.md")
    integration_compiler.manifest.chapters.append(c2)
    (integration_compiler.chapters_dir / "c2.md").write_text("Content 2", encoding="utf-8")
    
    full_text = integration_compiler._concatenate_chapters()
    assert "Content 1" in full_text
    assert "Content 2" in full_text

def test_compile_missing_assets(integration_compiler):
    """Test compilation when a referenced asset is missing."""
    # This checks logical robustness (warning log), real pandoc might just ignore or warn.
    base = integration_compiler.chapters_dir
    (base / "main.md").write_text("See ![img](missing.png)", encoding="utf-8")
    
    # We expect no crash
    integration_compiler.compile("pdf")
    assert integration_compiler.output_pdf.exists()
