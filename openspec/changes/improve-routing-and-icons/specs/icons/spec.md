# Spec Delta: UI Icons

## MODIFIED Requirements

### [Requirement: Icon Availability]
#### Description
Every interactive element with an icon must have a corresponding PNG file in `assets/icons`.

#### Scenario: Missing Icon Fallback
- **Given** a UI component requests an icon that does not exist.
- **When** `IconFactory.get_icon` is called.
- **Then** a warning must be logged and a visible placeholder (not just transparent) should be returned in debug mode.

#### Scenario: Icon Completeness
- **Given** the application is running.
- **When** the user views the Sidebar or Toolbar.
- **Then** all buttons must show their intended icons (no invisible buttons).

## ADDED Requirements

### [Requirement: Icon Generation]
#### Description
The design of all icons must be unique and representative of their function.

#### Scenario: Distinct Editing Icons
- **Given** the Toolbar is visible.
- **When** looking at Undo, Redo, and Quote buttons.
- **Then** each must have a distinct visual representation (not all the same).
