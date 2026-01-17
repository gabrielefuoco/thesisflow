# Capability: Breadcrumb Navigation

## ADDED Requirements

### Requirement: Hierarchical Context Display
A breadcrumb component SHALL display the current project, chapter, and (if applicable) paragraph hierarchy in the editor header.

#### Scenario: Navigating to a Chapter
- **GIVEN** a project "My Thesis" is open
- **WHEN** Chapter 1 "Introduction" is loaded
- **THEN** the breadcrumb should display `My Thesis > 1. Introduction`.

### Requirement: Dynamic Update
The breadcrumb SHALL update in real-time when the user switches between chapters or paragraphs.

#### Scenario: Switching to Paragraph
- **GIVEN** Chapter 1 is open
- **WHEN** Paragraph 1.1 "Background" is selected
- **THEN** the breadcrumb should update to `My Thesis > 1. Introduction > 1.1 Background`.
