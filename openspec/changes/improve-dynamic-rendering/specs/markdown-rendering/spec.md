# markdown-rendering Spec Delta

## MODIFIED Requirements

### Requirement: Optimized Instant Preview
The system SHALL update the side preview pane (if open) with a latency of less than 200ms after text changes, ensuring a smooth and responsive experience. **The rendering engine MUST support full GFM (GitHub Flavored Markdown) including tables and task lists.**

#### Scenario: Complex rendering
- **WHEN** the user types a markdown table or a nested list
- **THEN** the preview pane renders it correctly with proper alignment and styling
- **AND** the update occurs within 200ms

## ADDED Requirements

### Requirement: Themed HTML Preview
The preview pane SHALL automatically adapt its styling (colors, fonts, contrast) to match the currently selected application theme (Light or Dark).

#### Scenario: Theme switch
- **WHEN** the user switches the application theme from Light to Dark
- **THEN** the preview pane's background and text colors update immediately to match the new theme
- **AND** the fonts remain consistent with the editor's typography
