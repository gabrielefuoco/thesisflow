
import os
import shutil
import re
from pathlib import Path
from src.engine.project_manager import ProjectManager
from src.engine.compiler import CompilerEngine # Need compiler now

def test_orphan_handling():
    # Setup
    test_root = Path("test_run_orphans")
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir()

    pm = ProjectManager(projects_root=test_root)
    
    # Create Project
    try:
        proj_path = pm.create_project("Test Orphans", "Test Author")
        chapter = pm.manifest.chapters[0]
        
        # 1. Create a subsection manually (bypassing the fixed Create Subsection so it doesn't add the link)
        # We manually create the file to simulate an "old" orphan file
        sub_dir = proj_path / "chapters" / chapter.id
        sub_dir.mkdir(exist_ok=True, parents=True)
        orphan_file = sub_dir / "orphan_sub.md"
        orphan_file.write_text("## I am an orphan", encoding="utf-8")
        
        # 2. Run Compiler logic (simulate _concatenate_chapters)
        compiler = CompilerEngine(proj_path, pm.manifest)
        # We can't run full compile as we lack Pandoc/Typst on this env maybe, 
        # but we can test the internal method _concatenate_chapters matches logic
        
        print("Running concatenation...")
        full_text = compiler._concatenate_chapters()
        
        print("-" * 20)
        print("Concatenated Content:")
        print(full_text)
        print("-" * 20)
        
        if "## I am an orphan" in full_text:
            print("SUCCESS: Orphan file content found in output!")
        else:
            print(f"FAILURE: Orphan content not found.")
            exit(1)
            
    finally:
        # Cleanup
        if test_root.exists():
            shutil.rmtree(test_root)

if __name__ == "__main__":
    test_orphan_handling()
