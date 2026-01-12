## ADDED Requirements

### Requirement: Atomic Reference Parsing
The system SHALL parse the project's bibliography file(s) (e.g., `.bib`) into individual reference objects containing metadata (author, year, title, citation key).

#### Scenario: Load Project Bibliography
- **WHEN** a project is opened
- **THEN** the system SHALL parse the `references.bib` file and store a list of available citations in memory.

### Requirement: Citation Autocompletion
The editor SHALL provide an autocompletion menu for citations effectively triggered by a specific keystroke.

#### Scenario: Trigger Citation Menu
- **WHEN** the user types `@` in the editor
- **THEN** a dropdown menu SHALL appear listing all available references from the project bibliography.

#### Scenario: Filter Citations
- **WHEN** the citation menu is open and the user continues typing (e.g., `@Sm`)
- **THEN** the list SHALL filter to show only references matching the typed text (by author, title, or key).

#### Scenario: Insert Citation
- **WHEN** the user selects a reference from the menu
- **THEN** the editor SHALL insert the correct citation syntax (e.g., `@smith2023`) at the cursor position.
