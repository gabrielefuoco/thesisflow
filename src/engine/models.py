
from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path

@dataclass
class Chapter:
    id: str
    title: str
    filename: str

@dataclass
class ProjectManifest:
    title: str
    author: str
    candidate: str = ""
    supervisor: str = ""
    year: str = ""
    chapters: List[Chapter] = field(default_factory=list)

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "candidate": self.candidate,
            "supervisor": self.supervisor,
            "year": self.year,
            "chapters": [
                {"id": c.id, "title": c.title, "filename": c.filename}
                for c in self.chapters
            ]
        }

    @classmethod
    def from_dict(cls, data: dict):
        chapters = [Chapter(**c) for c in data.get("chapters", [])]
        return cls(
            title=data.get("title", "Untitled"),
            author=data.get("author", "Unknown"),
            candidate=data.get("candidate", ""),
            supervisor=data.get("supervisor", ""),
            year=data.get("year", ""),
            chapters=chapters
        )
