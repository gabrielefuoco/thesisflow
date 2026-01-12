# Project Context

## Purpose
ThesisFlow is an offline-first desktop application designed to streamline the academic writing process. It bridges the gap between the simplicity of Markdown and the professional typesetting of Typst.
**Core Philosophy:** "Focus on writing, let the engine handle the formatting."

## Tech Stack
- **Language:** Python 3.x
- **GUI Framework:** CustomTkinter (CTk)
- **Core Engine:** Custom Python logic for project management and compilation pipelines.
- **External Tools:**
  - **Pandoc:** Used for checking syntax and converting Markdown to intermediate formats.
  - **Typst:** The primary typesetting engine for generating high-quality PDFs.
- **Data Storage:** Local filesystem (JSON manifests, clear-text Markdown).
- **Testing:** Pytest, pytest-mock (high coverage on engine logic).

## Key Features
- **Distraction-Free Editor:** Markdown-based with syntax highlighting.
- **Project Structure:** Automated management of chapters, sections, and assets.
- **Live Preview:** Real-time feedback (simulated or rendered).
- **Bibliography Management:** Built-in BibTeX parsing and Crossref DOI resolution.
- **One-Click Compilation:** Automated pipeline (Markdown -> Typst -> PDF).

## Architecture Overview

### 1. Data Layer (FileSystem)
Projects are self-contained directories with the following structure:
- `.thesis_data/manifest.json`: Metadata (Title, Author, Chapter order).
- `chapters/`: Markdown content files.
  - Supports flat filenames (`chap_<id>.md`) or folders with `master.md`.
- `assets/`: Images and other media.
- `references.bib`: Project bibliographies.
- `master.typ`: The Typst entry point (template).

### 2. Engine Layer (`src.engine`)
- **ProjectManager:** Facade for all file system operations (CRUD Projects, Chapters, Assets). Handles ZIP import/export.
- **CompilerEngine:** Pipeline orchestrator.
  1. **Preprocessing:** Resolves custom `{{ include: ... }}` directives.
  2. **Conversion:** Uses Pandoc to convert concatenated Markdown to Typst.
  3. **Typesetting:** Invokes Typst to compile the final PDF.
- **Models:** Uses `dataclasses` (`ProjectManifest`, `Chapter`) for strong typing.

### 3. UI Layer (`src.ui`)
- **Dashboard:** Grid/List view of projects with "Recent" logic.
- **Editor:** Main writing interface using `CTkTextbox` with custom syntax highlighting capabilities.
- **Theme:** Centralized theming support (`src.ui.theme`).

## Conventions

### Code Style
- **Python:** PEP 8 enforced. 
- **Type Hints:** Required for all public methods in the Engine layer.
- **Naming:** `snake_case` for logic, `PascalCase` for UI Classes.

### Development Workflow
- **Tests First:** Engine modifications should be verified with `pytest tests/`.
- **Dependency Injection:** External tools (Pandoc/Typst) are wrapped in classes to allow mocking in tests.

## Domain Context
- **Academic Citation:** The system must handle CSL styles and BibTeX strictly.
- **Reproducibility:** Projects must be portable (ZIP export includes everything needed to compile).

## Important Constraints
- **Runtime Requirements:** User must have Pandoc and Typst installed and accessible in PATH (or configured).
- **Concurrency:** File operations assume single-user access; no complex locking mechanisms.

## External Dependencies
- `pandoc` (CLI)
- `typst` (CLI)

