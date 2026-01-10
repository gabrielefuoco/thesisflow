
import pytest
import shutil
from pathlib import Path
from src.engine.models import ProjectManifest, Chapter
from src.engine.project_manager import ProjectManager

@pytest.fixture
def temp_project_dir(tmp_path):
    """Creates a temporary directory for projects."""
    projects_root = tmp_path / "ThesisFlow_Projects"
    projects_root.mkdir()
    return projects_root

@pytest.fixture
def project_manager(temp_project_dir):
    """Returns a ProjectManager instance using the temp directory."""
    return ProjectManager(projects_root=temp_project_dir)

@pytest.fixture
def sample_manifest():
    """Returns a sample ProjectManifest."""
    return ProjectManifest(
        title="Test Thesis",
        author="Test Author",
        candidate="Test Candidate",
        supervisor="Test Supervisor",
        year="2024"
    )


