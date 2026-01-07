
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from src.engine.models import ProjectManifest, Chapter
from src.utils.paths import get_templates_dir

class ProjectManager:
    def __init__(self, projects_root: Path = None):
        if projects_root:
            self.projects_root = projects_root
        else:
             # Default to user documents
            self.projects_root = Path.home() / "Documents" / "ThesisFlow_Projects"
        
        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.current_project_path: Optional[Path] = None
        self.manifest: Optional[ProjectManifest] = None

    def list_projects(self) -> List[Path]:
        """Returns a list of valid project directories."""
        projects = []
        if not self.projects_root.exists():
            return []
            
        for d in self.projects_root.iterdir():
            if d.is_dir() and (d / ".thesis_data" / "manifest.json").exists():
                projects.append(d)
        return projects

    def create_project(self, name: str, author: str, template_path: Path = None) -> Path:
        """Creates a new project structure."""
        safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '_', '-')]).strip()
        project_dir = self.projects_root / safe_name
        
        if project_dir.exists():
            raise FileExistsError(f"Project '{safe_name}' already exists.")

        # Scaffolding
        (project_dir / ".thesis_data").mkdir(parents=True)
        (project_dir / "assets").mkdir()
        (project_dir / "chapters").mkdir()
        
        # Manifest
        manifest = ProjectManifest(title=name, author=author)
        self._save_manifest(project_dir, manifest)
        
        # Template Handling
        if template_path and template_path.exists():
            shutil.copy(template_path, target_master)
        else:
             # Default Master Template
            default_master = get_templates_dir() / "master_default.typ"
            if default_master.exists():
                shutil.copy(default_master, target_master)
            else:
                # Fallback
                target_master.write_text('#include ".thesis_data/temp/compiled_body.typ"', encoding="utf-8")
            
        self.current_project_path = project_dir
        self.manifest = manifest
        # Create first chapter default
        self.create_chapter("Capitolo 1: Introduzione")
        
        return project_dir

    def load_project(self, project_dir: Path):
        manifest_path = project_dir / ".thesis_data" / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError("Invalid project: manifest.json missing.")
        
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.manifest = ProjectManifest.from_dict(data)
        self.current_project_path = project_dir

    def create_chapter(self, title: str) -> Chapter:
        if not self.manifest or not self.current_project_path:
            raise RuntimeError("No project loaded.")

        cid = str(uuid.uuid4())[:8]
        filename = f"chap_{cid}.md"
        chapter = Chapter(id=cid, title=title, filename=filename)
        
        # Write file
        file_path = self.current_project_path / "chapters" / filename
        file_path.write_text(f"# {title}\n\nScrivi qui il tuo contenuto...", encoding="utf-8")
        
        self.manifest.chapters.append(chapter)
        self._save_manifest(self.current_project_path, self.manifest)
        return chapter

    def update_chapter_content(self, chapter: Chapter, content: str):
        if not self.current_project_path:
            raise RuntimeError("No project loaded")
        
        # Save content
        file_path = self.current_project_path / "chapters" / f"{chapter.id}.md"
        file_path.write_text(content, encoding="utf-8")

    def rename_chapter(self, chapter: Chapter, new_title: str):
        if not self.manifest: return
        # Update model
        chapter.title = new_title
        # Save manifest
        self._save_manifest(self.current_project_path, self.manifest)
        
        # Optionally update content header if it exists?
        # Let's keep it simple: just metadata rename.
        
    def delete_chapter(self, chapter: Chapter):
        if not self.manifest: return
        
        # Remove from list
        self.manifest.chapters = [c for c in self.manifest.chapters if c.id != chapter.id]
        self._save_manifest(self.current_project_path, self.manifest)
        
        # Remove file
        file_path = self.current_project_path / "chapters" / chapter.filename
        if file_path.exists():
            file_path.unlink()

    def move_chapter(self, chapter: Chapter, direction: str):
        """Moves a chapter 'up' or 'down' in the list."""
        if not self.manifest: return
        
        idx = -1
        for i, c in enumerate(self.manifest.chapters):
            if c.id == chapter.id:
                idx = i
                break
        
        if idx == -1: return

        new_idx = idx
        if direction == "up" and idx > 0:
            new_idx = idx - 1
        elif direction == "down" and idx < len(self.manifest.chapters) - 1:
            new_idx = idx + 1
        
        if new_idx != idx:
            # Swap
            self.manifest.chapters[idx], self.manifest.chapters[new_idx] = self.manifest.chapters[new_idx], self.manifest.chapters[idx]
            self._save_manifest(self.current_project_path, self.manifest)

    def get_chapter_content(self, chapter: Chapter) -> str:
        if not self.current_project_path:
             return ""
        path = self.current_project_path / "chapters" / chapter.filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _save_manifest(self, project_dir: Path, manifest: ProjectManifest):
        path = project_dir / ".thesis_data" / "manifest.json"
        path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")

    def add_asset(self, source_path: Path) -> str:
        """Copies an asset file to the project assets directory and returns relative path."""
        if not self.current_project_path:
            raise ValueError("No project loaded")
        
        assets_dir = self.current_project_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        dest_path = assets_dir / source_path.name
        # Simple copy
        import shutil
        shutil.copy2(source_path, dest_path)
        
        # Return path relative to project root (standard markdown format)
        return f"assets/{source_path.name}"

    def export_project(self, project_path: Path, dest_zip: Path):
        """Archives the project folder to a zip file."""
        import shutil
        # make_archive works on the root_dir. 
        # project_path is c:/.../MyProject
        # we want zip to contain MyProject/... or just contents? 
        # Usually import expects a folder. Let's zip the content to keep it simple, 
        # or zip the folder itself. 
        # Best practice: zip the folder so extracting gives you the folder.
        
        base_name = str(dest_zip).replace(".zip", "")
        shutil.make_archive(base_name, 'zip', root_dir=project_path.parent, base_dir=project_path.name)

    def import_project(self, zip_path: Path) -> Path:
        """Extracts a zip project to the projects directory. Returns path to extracted project."""
        import shutil
        import zipfile
        
        # Check if valid zip
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Not a valid zip file")

        # Destination
        dest_dir = self.projects_root
        
        # We need to handle potential naming conflicts or weird zip structures.
        # Assuming the zip contains a single root folder "MyProject/"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Inspection could be complex. Let's just extract.
            # If the user zipped the *contents* (manifest.json at root of zip), we need a folder.
            # If user zipped the *folder*, we get MyProject/manifest.json.
            
            # Heuristic: Check first file
            first = zf.infolist()[0].filename
            is_folder_packed = '/' in first and not first.startswith('__MACOSX')
            
            if is_folder_packed:
                # Extract as is
                zf.extractall(dest_dir)
                # Find what we extracted? 
                extracted_name = first.split('/')[0]
                return dest_dir / extracted_name
            else:
                # Contents packed. Create a folder based on zip name
                name = zip_path.stem
                new_project_path = dest_dir / name
                new_project_path.mkdir(exist_ok=True)
                zf.extractall(new_project_path)
                return new_project_path
