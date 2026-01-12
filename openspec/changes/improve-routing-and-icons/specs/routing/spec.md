# Spec Delta: Centralized Routing

## ADDED Requirements

### [Requirement: View Routing]
#### Description
View transitions must be managed by a centralized router to ensure consistency and state management.

#### Scenario: Navigate to Dashboard
- **Given** the user is in the Editor.
- **When** the "Back" button is clicked.
- **Then** the router must trigger the dashboard view and ensure the current project project state is cleared or safely stored.

#### Scenario: Prevent Navigation Data Loss
- **Given** the editor has unsaved changes.
- **When** a navigation event is triggered.
- **Then** the router must ensure the `save_current_file` logic is executed before switching the view.

### [Requirement: Consistent Navigation API]
#### Description
UI components must trigger navigation using a unified API.

#### Scenario: Component-Triggered Navigation
- **Given** a component needs to change the view (e.g., Sidebar opening Bibliography).
- **When** it calls `navigate("bibliography")`.
- **Then** the router must handle the `grid_forget`/`grid` sequence automatically.
