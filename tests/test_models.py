
import pytest
from src.engine.models import ProjectManifest, Chapter

def test_chapter_model():
    """Test Chapter dataclass initialization."""
    c = Chapter(id="123", title="Intro", filename="intro.md")
    assert c.id == "123"
    assert c.title == "Intro"
    assert c.filename == "intro.md"

def test_manifest_defaults():
    """Test ProjectManifest default values."""
    m = ProjectManifest(title="T", author="A")
    assert m.citation_style == "ieee.csl"
    assert m.chapters == []

def test_manifest_serialization():
    """Test to_dict and from_dict for ProjectManifest."""
    c1 = Chapter(id="c1", title="C1", filename="c1.md")
    m = ProjectManifest(
        title="My Thesis",
        author="Me",
        candidate="Cand",
        supervisor="Sup",
        year="2024",
        chapters=[c1],
        citation_style="apa.csl"
    )
    
    data = m.to_dict()
    assert data["title"] == "My Thesis"
    assert data["chapters"][0]["id"] == "c1"
    
    m2 = ProjectManifest.from_dict(data)
    assert m2.title == m.title
    assert m2.chapters[0].title == c1.title
    assert m2.citation_style == "apa.csl"

def test_manifest_empty_chapters_load():
    """Test loading manifest with missing chapters key."""
    data = {"title": "T", "author": "A"}
    m = ProjectManifest.from_dict(data)
    assert m.chapters == []
