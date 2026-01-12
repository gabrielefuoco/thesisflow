import bibtexparser
from typing import List, Dict, Optional

class BibParser:
    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
            return bib_database.entries
        except Exception as e:
            print(f"Error parsing bib file: {e}")
            return []

    @staticmethod
    def parse_string(bib_string: str) -> List[Dict]:
        try:
            bib_database = bibtexparser.loads(bib_string)
            return bib_database.entries
        except Exception as e:
            print(f"Error parsing bib string: {e}")
            return []
