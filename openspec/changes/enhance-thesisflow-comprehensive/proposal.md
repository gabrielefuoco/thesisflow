# Change: Enhance IsFlow Comprehensive

## Why
ThesisFlow currently provides a solid foundation for offline academic writing but lacks the polish and robust feature set expected of a modern desktop application. The user interface can be improved for better usability, and the underlying engine needs to be more resilient and capable of handling complex projects. Improving "every aspect" ensures the tool becomes a viable alternative to other Markdown editors.

## What Changes
- **UI/UX Overhaul**:
  - [ ] Implement a cohesive design system with consistent typography and spacing.
  - [ ] Add a responsive sidebar for project navigation.
  - [ ] Improve dark/light mode consistency.
- **Project Management**:
  - [ ] Add "Export to ZIP" and "Import from ZIP" directly in the dashboard.
  - [ ] Implement "Duplicate Project".
- **Editor Enhancements**:
  - [ ] Add auto-save functionality with configurable intervals.
  - [ ] Implement a status bar showing word count and compilation status.
  - [ ] Add basic find/replace functionality.
  - [ ] Implement smart citation autocompletion using `@` trigger.
- **Bibliography Management**:
  - [ ] Parse project references as atomic objects.
  - [ ] Support real-time filtering of references during citation.
- **Engine Robustness**:
  - [ ] Asynchronous compilation to prevent UI freezing.
  - [ ] Detailed error reporting for Pandoc/Typst failures (parsing stderr).
  - [ ] Support for multiple bibliography files.
- **Architecture**:
  - [ ] Refactor into a stricter Model-View-Controller (MVC) pattern to separate UI logic from business logic.
  - [ ] Introduce a global `StateManager` for handling application-wide state (settings, active project).

## Impact
- **Affected Specs**: `project-management`, `editor`, `engine`, `ui-shell` (New capabilities).
- **Affected Code**: Almost all files in `src/ui` and `src/engine`.
- **Breaking Changes**:
  - Project manifest format might be updated to support new metadata (e.g., autosave settings per project).
