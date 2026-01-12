## ADDED Requirements

### Requirement: Project Export
The system SHALL allow users to export an entire project (including assets and manifest) to a single ZIP file.

#### Scenario: Export Project
- **WHEN** the user clicks "Export" on a project card
- **THEN** a ZIP file containing the full project structure SHALL be created at the user-selected location.

### Requirement: Project Import
The system SHALL allow users to import a project from a ZIP file derived from a valid ThreadFlow export.

#### Scenario: Import Project
- **WHEN** the user selects "Import" and chooses a valid project ZIP
- **THEN** the project SHALL be extracted to the workspace and appear in the dashboard.
