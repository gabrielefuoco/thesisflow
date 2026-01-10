
import pytest
from src.ui.bibliography import CitationDialog

def test_bibtex_parsing_simple():
    """Test parsing a standard BibTeX entry."""
    bibtex = """@article{smith2023,
    title = {Deep Learning},
    author = {Smith, John},
    year = {2023},
    journal = {AI Journal},
    doi = {10.1234/5678}
}"""
    
    data = CitationDialog.parse_bibtex(bibtex)
    
    assert data["type"] == "article"
    assert data["fields"]["id"] == "smith2023"
    assert data["fields"]["title"] == "Deep Learning"
    assert data["fields"]["author"] == "Smith, John"
    assert data["fields"]["year"] == "2023"
    assert data["fields"]["publisher"] == "AI Journal"
    assert data["fields"]["doi"] == "10.1234/5678"

def test_bibtex_parsing_book_quotes():
    """Test parsing with quotes instead of braces."""
    bibtex = """@book{doe2020,
    title = "My Book",
    publisher = "PubCo"
}"""
    data = CitationDialog.parse_bibtex(bibtex)
    assert data["fields"]["title"] == "My Book"
    assert data["fields"]["publisher"] == "PubCo"

def test_bibtex_malformed():
    """Test parsing malformed BibTeX gracefully."""
    # Missing closure
    bibtex = "@article{key, title={Incomplete}" 
    data = CitationDialog.parse_bibtex(bibtex)
    assert data["type"] == "article" 
    assert data["fields"]["title"] == "Incomplete" # Regex might still catch it

def test_bibtex_empty_fields():
    """Test parsing fields with empty values."""
    bibtex = "@book{k,\n title={},\n year={}\n}"
    data = CitationDialog.parse_bibtex(bibtex)
    assert data["fields"]["title"] == ""
    assert data["fields"]["year"] == ""
