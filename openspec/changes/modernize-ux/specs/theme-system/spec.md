# Capability: Theme System

## ADDED Requirements

### Requirement: Modern Palette Definition
The theme SHALL define a modern, HSL-based color palette for both Light and Dark modes.

#### Scenario: Dark Mode Aesthetic
- **WHEN** the application is set to "Dark" mode
- **THEN** the background color should be a deep slate (`#0f172a`) and accents should be vibrant teal (`#14b8a6`).

### Requirement: Semantic Color Access
UI components SHALL access colors via semantic keys (e.g., `PANEL`, `ACCENT`) rather than hardcoded values.

#### Scenario: Component Theming
- **GIVEN** a new CTK component is created
- **WHEN** it requests `Theme.COLOR_ACCENT`
- **THEN** it must receive the correct hex code for the current mode.
