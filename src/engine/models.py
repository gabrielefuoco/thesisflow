
from dataclasses import dataclass, field
from typing import List, Optional
import json
from pathlib import Path

@dataclass
class Paragraph:
    id: str
    title: str
    filename: str

@dataclass
class Chapter:
    id: str
    title: str
    filename: str
    paragraphs: List[Paragraph] = field(default_factory=list)

@dataclass
class ProjectManifest:
    title: str
    author: str
    candidate: str = ""
    supervisor: str = ""
    year: str = ""
    chapters: List[Chapter] = field(default_factory=list)
    citation_style: str = "ieee.csl" # Default style

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "candidate": self.candidate,
            "supervisor": self.supervisor,
            "year": self.year,
            "chapters": [
                {
                    "id": c.id, 
                    "title": c.title, 
                    "filename": c.filename,
                    "paragraphs": [{"id": p.id, "title": p.title, "filename": p.filename} for p in c.paragraphs]
                }
                for c in self.chapters
            ],
            "citation_style": self.citation_style
        }

    @classmethod
    def from_dict(cls, data: dict):
        chapters = []
        for c_data in data.get("chapters", []):
            paragraphs = [Paragraph(**p) for p in c_data.get("paragraphs", [])]
            # Handle potential missing paragraphs field in older manifests
            c_data_copy = c_data.copy()
            if "paragraphs" in c_data_copy:
                del c_data_copy["paragraphs"]
            chapters.append(Chapter(**c_data_copy, paragraphs=paragraphs))
            
        return cls(
            title=data.get("title", "Untitled"),
            author=data.get("author", "Unknown"),
            candidate=data.get("candidate", ""),
            supervisor=data.get("supervisor", ""),
            year=data.get("year", ""),
            chapters=chapters,
            citation_style=data.get("citation_style", "ieee.csl")
        )
