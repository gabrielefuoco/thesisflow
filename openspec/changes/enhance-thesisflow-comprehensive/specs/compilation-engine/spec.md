## ADDED Requirements

### Requirement: Asynchronous Compilation
The system SHALL perform document compilation in a background thread to prevent blocking the UI.

#### Scenario: Compile large document
- **WHEN** the user triggers a compilation
- **THEN** the UI SHALL remain responsive (e.g., clickable, movable) while the compilation runs.

### Requirement: Error Reporting
The system SHALL parse standard error output from Pandoc and Typst to present user-friendly error messages.

#### Scenario: Typst Syntax Error
- **WHEN** compilation fails due to a Typst syntax error
- **THEN** the system SHALL display a readable error message indicating the file and line number, extracted from the `stderr`.
