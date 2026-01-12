# Design: Comprehensive Enhancements

## Context
ThesisFlow is a Python/CustomTkinter desktop app. The current codebase has a basic separation of concerns but mixes UI and logic in some places. The goal is to modernize the app without rewriting the core `pandoc`/`typst` pipeline integration.

## Goals / Non-Goals
- **Goals**:
  - Improve UI responsiveness and aesthetics.
  - specific feature additions (Auto-save, Export/Import).
  - Better error handling.
- **Non-Goals**:
  - Rewriting the UI in a web-based framework (Electron/Tauri) - we are sticking to Python/CTk for now as per current stack.
  - Multi-user collaboration.

## Decisions
- **Architecture Pattern**: We will enforce a robust Controller layer.
  - `View` classes (`src.ui`) should only handle display and user input forwarding.
  - `Controller` classes (`src.controllers`) will handle business logic and bridge `View` and `Engine`.
  - `Engine` classes (`src.engine`) remain pure logic/IO, unaware of UI.
- **Bibliography Handling**:
  - We will implement a `BibliographyService` that parses `.bib` files into a list of reference objects.
  - The Editor view will intercept `@` keystrokes to trigger a `CitationPopup` (overlay) populated by the service.
- **Async Operations**:
  - Compilation will move to a `threading.Thread` or `concurrent.futures` execution to keep the GUI responsive.
  - CTk's `after` method will be used to poll for completion or receive callbacks.

## Risks / Trade-offs
- **Risk**: Refactoring to strict MVC might introduce regressions in existing features.
  - **Mitigation**: Comprehensive manual testing and ensuring unit tests for Engine remain passing.
- **Risk**: CustomTkinter limitations for advanced editor features (like semantic syntax highlighting performance).
  - **Mitigation**: Keep highlighting simple (regex-based) or accept some latency for large files.

## Migration Plan
1. Refactor `ProjectManager` and related engine classes to be isolated.
2. Create Controller classes.
3. Update Views to use Controllers.
4. Implement new features on top of the new architecture.
