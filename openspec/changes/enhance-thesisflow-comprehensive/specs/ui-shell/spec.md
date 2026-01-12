## ADDED Requirements

### Requirement: Responsive Layout
The application main window SHALL be divided into a sidebar (navigation) and a main content area, with the sidebar being collapsible or resizable.

#### Scenario: Resize window
- **WHEN** the user resizes the application window
- **THEN** the sidebar and content area SHALL adjust their width proportionally or maintain fixed sidebar width while content expands.

### Requirement: Theme System
The application SHALL support switching between "Light", "Dark", and "System" themes, affecting all UI components consistently.

#### Scenario: Switch to Dark Mode
- **WHEN** the user selects "Dark Mode" in settings
- **THEN** the background, text, and component colors SHALL update to the defined dark palette immediately.
