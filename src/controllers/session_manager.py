from typing import Optional
from pathlib import Path

class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        
        self.active_project_path: Optional[Path] = None
        self.settings: dict = {}
        # Add other global state here
    
    def set_active_project(self, path: Path):
        self.active_project_path = path
        
    def get_active_project(self) -> Optional[Path]:
        return self.active_project_path
