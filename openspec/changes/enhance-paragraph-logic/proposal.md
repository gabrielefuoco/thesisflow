# Proposal: Enhance Paragraph Logic and Automatic Numbering

## Goal
Improve the management of subsections (referred to as "paragraphs" by the user) by introducing a native model for them in the manifest. Implement automatic numbering visible in both the GUI and the exported PDF.

## Context
Currently, subsections are loose files on disk included via a custom syntax. They are not tracked in the manifest, making hierarchical numbering and management difficult. The PDF export also lacks structured heading levels for these subsections.

## Scopes
- **Core Models**: Introduction of `Paragraph` model and hierarchy in `ProjectManifest`.
- **Project Logistics**: Refactoring `ProjectManager` to handle paragraph CRUD with manifest persistence.
- **GUI**: Updating the sidebar and editor headers to show automatic numbering.
- **Compiler**: Improving the MD-to-Typst pipeline to correctly rank headings and enable numbering in the final PDF.

## Design Highlights
- Chapters will remain Level 1 headings.
- Paragraphs will be Level 2 headings.
- Numbering will be handled dynamically in the GUI and via Typst's `set heading(numbering: "1.1")` in the PDF.
