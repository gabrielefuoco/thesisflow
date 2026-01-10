
import os
import shutil
from pathlib import Path
from src.engine.project_manager import ProjectManager

def test_subsection_include():
    # Setup
    test_root = Path("test_run_temp")
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir()

    pm = ProjectManager(projects_root=test_root)
    
    # Create Project
    try:
        proj_path = pm.create_project("Test Thesis", "Test Author")
        print(f"Project created at {proj_path}")
        
        # Get the first default chapter
        chapter = pm.manifest.chapters[0]
        print(f"Testing on chapter: {chapter.title} ({chapter.filename})")
        
        # Create Subsection
        sub_title = "My New Section"
        pm.create_subsection(chapter, sub_title)
        
        # Verify
        chapter_file = proj_path / "chapters" / chapter.filename
        content = chapter_file.read_text("utf-8")
        
        expected_include = f"{{{{ include: {chapter.id}/My_New_Section.md }}}}"
        
        print("-" * 20)
        print("Chapter Content:")
        print(content)
        print("-" * 20)
        
        if expected_include in content:
            print("SUCCESS: Include directive found!")
        else:
            print(f"FAILURE: Expected '{expected_include}' not found.")
            exit(1)
            
    finally:
        # Cleanup
        if test_root.exists():
            shutil.rmtree(test_root)

if __name__ == "__main__":
    test_subsection_include()
