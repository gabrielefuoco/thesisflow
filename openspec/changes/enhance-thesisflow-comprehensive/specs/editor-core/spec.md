## ADDED Requirements

### Requirement: Auto-Save
The editor SHALL automatically save the currently open file after a configurable period of inactivity or periodically.

#### Scenario: Auto-save triggers
- **WHEN** the user modifies the document and waits for 5 seconds (default)
- **THEN** the changes SHALL be written to disk automatically without user intervention.

### Requirement: Status Bar
The editor SHALL display a status bar at the bottom of the window showing the current word count and cursor position.

#### Scenario: Typing text
- **WHEN** the user types in the editor
- **THEN** the word count displayed in the status bar SHALL update in real-time.
