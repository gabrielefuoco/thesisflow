from pathlib import Path
from typing import List, Optional
from src.engine.project_manager import ProjectManager
from src.controllers.session_manager import SessionManager

class ProjectController:
    def __init__(self):
        self.pm = ProjectManager()
        self.session = SessionManager()

    def list_projects(self) -> List[Path]:
        return self.pm.list_projects()

    def create_project(self, name: str, author: str, template_path: Path = None, **kwargs) -> Path:
        path = self.pm.create_project(name, author, template_path)
        # Update extra settings if provided
        if kwargs:
            self.pm.update_settings(kwargs)
        return path

    def load_project(self, path: Path):
        self.pm.load_project(path)
        self.session.set_active_project(path)

    def export_project(self, project_path: Path, dest_zip: Path):
        self.pm.export_project(project_path, dest_zip)

    def import_project(self, zip_path: Path) -> Path:
        return self.pm.import_project(zip_path)

    def delete_project(self, project_path: Path):
        self.pm.delete_project(project_path)
        if self.session.get_active_project() == project_path:
            self.session.set_active_project(None)
            
    def get_citation_styles(self) -> List[str]:
        return self.pm.list_citation_styles()
        
    def get_templates(self) -> List[str]:
        return self.pm.list_templates()
