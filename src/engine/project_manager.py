
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

    def create_project(self, name: str, author: str) -> Path:
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
        
        # Default Master Template
        # In a real app we'd copy from templates, for now we create a basic one or copy key parts
        default_master = get_templates_dir() / "master_default.typ"
        target_master = project_dir / "master.typ"
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
             return
        path = self.current_project_path / "chapters" / chapter.filename
        path.write_text(content, encoding="utf-8")

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
        """Copies an asset to the project's asset folder and returns specific markdown-ready path."""
        if not self.current_project_path:
            raise RuntimeError("No project loaded.")
        
        assets_dir = self.current_project_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        target_path = assets_dir / source_path.name
        # Simple collision avoidance could be added here
        shutil.copy(source_path, target_path)
        
        # Return relative path for use in Markdown (e.g. "assets/image.png")
        return f"assets/{source_path.name}"
