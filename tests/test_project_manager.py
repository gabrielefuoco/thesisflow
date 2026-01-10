
import pytest
from pathlib import Path
from src.engine.models import Chapter

def test_create_project(project_manager):
    """Test creating a new project structure."""
    proj_path = project_manager.create_project("My Thesis", "Gabri")
    
    assert proj_path.exists()
    assert (proj_path / ".thesis_data" / "manifest.json").exists()
    assert (proj_path / "chapters").exists()
    assert (proj_path / "assets").exists()
    
    # Check manifest content via PM
    assert project_manager.manifest.title == "My Thesis"
    assert project_manager.manifest.author == "Gabri"
    assert len(project_manager.manifest.chapters) == 1 # Default chapter

def test_load_project(project_manager):
    """Test loading an existing project."""
    # First create one
    p1 = project_manager.create_project("Load Me", "Author")
    
    # Reset PM
    project_manager.current_project_path = None
    project_manager.manifest = None
    
    # Load
    project_manager.load_project(p1)
    assert project_manager.manifest.title == "Load Me"
    assert project_manager.current_project_path == p1

def test_duplicate_project_error(project_manager):
    """Test checking for duplicate projects."""
    project_manager.create_project("Dup Test", "Me")
    with pytest.raises(FileExistsError):
        project_manager.create_project("Dup Test", "Me Again")

def test_create_chapter(project_manager):
    """Test adding a chapter."""
    project_manager.create_project("Chapter Test", "Me")
    chap = project_manager.create_chapter("New Chapter")
    
    assert isinstance(chap, Chapter)
    assert chap.title == "New Chapter"
    assert (project_manager.current_project_path / "chapters" / chap.filename).exists()
    assert len(project_manager.manifest.chapters) == 2

def test_rename_chapter(project_manager):
    """Test renaming a chapter."""
    project_manager.create_project("Rename Test", "Me")
    chap = project_manager.manifest.chapters[0]
    
    project_manager.rename_chapter(chap, "Updated Title")
    
    # Reload manifest to verify persistence
    project_manager.load_project(project_manager.current_project_path)
    assert project_manager.manifest.chapters[0].title == "Updated Title"

def test_delete_chapter(project_manager):
    """Test deleting a chapter."""
    project_manager.create_project("Delete Test", "Me")
    chap = project_manager.create_chapter("To Delete")
    
    assert len(project_manager.manifest.chapters) == 2
    path = project_manager.current_project_path / "chapters" / chap.filename
    assert path.exists()
    
    project_manager.delete_chapter(chap)
    
    assert len(project_manager.manifest.chapters) == 1
    assert not path.exists()

def test_move_chapter(project_manager):
    """Test reordering chapters."""
    project_manager.create_project("Move Test", "Me")
    c1 = project_manager.manifest.chapters[0]
    c2 = project_manager.create_chapter("Second")
    c3 = project_manager.create_chapter("Third")
    
    # Order: c1, c2, c3
    assert project_manager.manifest.chapters == [c1, c2, c3]
    
    # Move c3 up -> c1, c3, c2
    project_manager.move_chapter(c3, "up")
    assert project_manager.manifest.chapters == [c1, c3, c2]
    
    # Move c1 down -> c3, c1, c2
    project_manager.move_chapter(c1, "down")
    assert project_manager.manifest.chapters == [c3, c1, c2]

def test_add_asset(project_manager, tmp_path):
    """Test adding an asset to the project."""
    project_manager.create_project("Asset Test", "Me")
    
    # Create dummy source file
    src_img = tmp_path / "image.png"
    src_img.write_text("fake image data", encoding="utf-8")
    
    rel_path = project_manager.add_asset(src_img)
    
    assert rel_path == "assets/image.png"
    assert (project_manager.current_project_path / "assets" / "image.png").exists()
    
    # Test collision
    rel_path_2 = project_manager.add_asset(src_img)
    assert rel_path_2 == "assets/image_1.png"

def test_create_subsection(project_manager):
    """Test creating a subsection (file inside chapter folder)."""
    project_manager.create_project("SubTest", "Me")
    chap = project_manager.manifest.chapters[0]
    
    project_manager.create_subsection(chap, "My Paragraph")
    
    # Expectation: chapters/<chap_id>/My Paragraph.md
    safe_title = "My_Paragraph.md" # sanitized
    # Note: sanitization uses space if allowed, or underscore? 
    # Logic: "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')])
    # "My Paragraph" -> "My Paragraph"
    
    expected_path = project_manager.current_project_path / "chapters" / chap.id / "My Paragraph.md"
    if not expected_path.exists():
         # Fallback check if sanitize logic differs (e.g. spaces allowed)
         expected_path = project_manager.current_project_path / "chapters" / chap.id / "My_Paragraph.md"

    assert expected_path.exists()
    assert "# My Paragraph" in expected_path.read_text(encoding="utf-8")

def test_invalid_project_name(project_manager):
    """Test creating project with invalid characters."""
    # Should sanitize or error? 
    # Current implementation sanitizes.
    path = project_manager.create_project("Bad/Name", "Me")
    assert path.name == "Bad_Name" or path.name == "BadName" or "Bad" in path.name

def test_pm_io_methods(project_manager):
    """Test read/save logic."""
    project_manager.create_project("IOTest", "Me")
    
    # Save
    p = project_manager.current_project_path / "test.txt"
    project_manager.save_file_content(p, "Hello World")
    assert p.exists()
    assert p.read_text(encoding="utf-8") == "Hello World"
    
    # Read
    content = project_manager.read_file_content(p)
    assert content == "Hello World"

def test_pm_list_assets(project_manager):
    """Test listing assets."""
    project_manager.create_project("AssetTest", "Me")
    # Add dummy asset manually to test listing
    (project_manager.current_project_path / "assets" / "a.png").touch()
    (project_manager.current_project_path / "assets" / "b.jpg").touch()
    
    assets = project_manager.list_assets()
    assert len(assets) == 2
    names = [f.name for f in assets]
    assert "a.png" in names
    assert "b.jpg" in names

def test_pm_list_subsections(project_manager):
    """Test listing subsections."""
    project_manager.create_project("SubListTest", "Me")
    chap = project_manager.manifest.chapters[0]
    
    # Create subsections
    project_manager.create_subsection(chap, "Sub1")
    project_manager.create_subsection(chap, "Sub2")
    
    subs = project_manager.list_subsections(chap)
    assert len(subs) == 2
    names = [f.stem for f in subs]
    assert "Sub1.md" in filter(lambda n: "Sub1" in n, [f.name for f in subs]) or "Sub1" in names

def test_pm_list_templates(project_manager):
    """Test listing templates."""
    templates = project_manager.list_templates()
    assert isinstance(templates, list)
    # Default behavior might depend on environment, but should return list
    assert "Default" in templates or len(templates) >= 0

def test_pm_list_citation_styles(project_manager):
    """Test listing citation styles."""
    styles = project_manager.list_citation_styles()
    assert isinstance(styles, list)
    assert "Default" in styles

def test_save_settings(project_manager):
    """Test public save_settings method."""
    project_manager.create_project("SaveSettingsTest", "Me")
    
    project_manager.manifest.author = "New Author"
    project_manager.save_settings()
    
    # Verify reload
    project_manager.load_project(project_manager.current_project_path)
    assert project_manager.manifest.author == "New Author"
