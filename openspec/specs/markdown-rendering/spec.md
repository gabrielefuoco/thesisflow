# markdown-rendering Specification

## Purpose
TBD - created by archiving change implement-instant-markdown-rendering. Update Purpose after archive.
## Requirements
### Requirement: Live Preview Editor
The editor SHALL provide an Obsidian-like "Live Preview" experience by eliding markdown syntax characters when the cursor is not active on the line and applying the corresponding formatting.

#### Scenario: Heading rendering and elision
- **WHEN** the user types `# Heading` on a line
- **THEN** the line font increases to the theme's H1 size
- **AND** the `# ` remains visible while the cursor is on the line
- **AND** the `# ` becomes hidden (elided) when the cursor leaves the line

#### Scenario: Bold text rendering and elision
- **WHEN** the user wraps text in `**` (e.g., `**bold**`)
- **THEN** the text `bold` is displayed with a bold weight
- **AND** the `**` markers are hidden when the cursor is not on that line

### Requirement: Optimized Instant Preview
The system SHALL update the side preview pane (if open) with a latency of less than 200ms after text changes, ensuring a smooth and responsive experience.

#### Scenario: Instant update
- **WHEN** the user types in the editor
- **THEN** the preview pane reflects the changes nearly instantaneously without noticeable flicker or lag

