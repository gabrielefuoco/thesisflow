from pathlib import Path
from typing import List, Dict, Optional
from src.engine.bib_parser import BibParser

class BibliographyService:
    def __init__(self):
        self.references: List[Dict] = []
        self._cache_path: Optional[Path] = None

    def load_bibliography(self, path: Path):
        self._cache_path = path
        if path.exists():
            self.references = BibParser.parse_file(str(path))
        else:
            self.references = []

    def get_references(self) -> List[Dict]:
        return self.references

    def search(self, query: str) -> List[Dict]:
        if not query: return self.references
        q = query.lower()
        results = []
        for ref in self.references:
            # Search in common fields
            if (q in ref.get('title', '').lower() or 
                q in ref.get('author', '').lower() or 
                q in ref.get('ID', '').lower()):
                results.append(ref)
        return results

    def get_citation_keys(self) -> List[str]:
        return [f"@{ref['ID']}" for ref in self.references if 'ID' in ref]
