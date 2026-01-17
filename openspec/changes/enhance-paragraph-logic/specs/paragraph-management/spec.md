# Capability: Paragraph Management

## ADDED Requirements

### Requirement: Structured Paragraph Model
The system MUST track subsections (paragraphs) as first-class objects within chapters in the project manifest.

#### Scenario: Creating a Paragraph
- **Given** an open project with at least one chapter
- **When** the user creates a new "Sezione" (Paragraph)
- **Then** a new MD file is created in a subdirectory `chapters/<chapter_id>/`
- **And** the paragraph is added to the `paragraphs` list of the chapter in `manifest.json`

### Requirement: Automatic Numbering in GUI
The GUI MUST display hierarchical numbers for chapters and paragraphs.

#### Scenario: Displaying Sidebar Numbering
- **Given** a project with 2 chapters, where Chapter 1 has 2 paragraphs
- **Then** the sidebar should show:
    - "1. Introduction"
        - "1.1 Background"
        - "1.2 Objectives"
    - "2. Literature Review"

### Requirement: Hierarchical PDF Numbering
The exported PDF MUST use hierarchical numbering for headings, corresponding to chapters (Level 1) and paragraphs (Level 2).

#### Scenario: Exporting to PDF
- **Given** a project with structured paragraphs
- **When** the user clicks "PUBBLICA PDF"
- **Then** the compiler should generate Typst headings `= Title` for chapters and `== Title` for paragraphs
- **And** the Typst output MUST have `set heading(numbering: "1.1")` enabled
