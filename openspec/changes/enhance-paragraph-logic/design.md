# Design: Paragraph Management and Numbering

## Data Model
We will update `src/engine/models.py` to include a `Paragraph` dataclass.

```python
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
```

## Numbering System
- **GUI**: The `SidebarFrame` will iterate through `manifest.chapters`. For each chapter `i` (1-indexed) and each paragraph `j` (1-indexed), it will display `i.j`.
- **PDF**: The `master.typ` (or the compilation body) will include Typst directives:
  ```typst
  #set heading(numbering: "1.1")
  ```
  Chapters will be generated as `= Title` (Level 1) and Paragraphs as `== Title` (Level 2).

## Migration Strategy
Existing sub-sections are identified by `{{ include: cid/filename.md }}` in the chapter's master file.
A migration utility or a lazy-loading logic in `ProjectManager` will move these into the `paragraphs` list in the manifest.

## Compiler Changes
The `_resolve_includes` logic in `ProjectManager` will be refactored to use the manifest structure instead of regex-searching for includes, ensuring a more robust and ordered merge of content.
