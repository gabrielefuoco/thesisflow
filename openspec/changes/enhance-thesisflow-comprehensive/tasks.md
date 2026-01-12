## 1. Architecture Refactoring
- [ ] 1.1 Create `src/controllers` package.
- [ ] 1.2 Move application state management to `src.controllers.SessionManager`.
- [ ] 1.3 Refactor `Dashboard` to use `ProjectController`.

## 2. UI/UX Overhaul
- [ ] 2.1 Update Main Window layout (Sidebar + Content area).
- [ ] 2.2 Implement consistent Theme definition (Color palette).
- [ ] 2.3 Refactor Editor view to be more modular.

## 3. Editor Features
- [ ] 3.1 Implement `AutoSaveService` in `src.engine`.
- [ ] 3.2 Add Status Bar component to Editor.
- [ ] 3.3 Add "Find and Replace" dialog.
- [ ] 3.4 Implement citation autocompletion (listener for `@` key).
- [ ] 3.5 Create `CitationPopup` UI component.

## 4. Bibliography Management
- [ ] 4.1 Implement `BibParser` in `src.engine` (using `bibtexparser` or similar).
- [ ] 4.2 Create `BibliographyService` to cache and search references.

## 5. Project Management Features
- [ ] 4.1 Implement `export_project_zip` in `ProjectManager`.
- [ ] 4.2 Implement `import_project_zip` logic.
- [ ] 4.3 Add UI controls for Import/Export in Dashboard.

## 5. Engine & Compilation
- [ ] 5.1 Create `AsyncCompiler` wrapper.
- [ ] 5.2 Parse `typst` stderr output for friendly error messages.
- [ ] 5.3 Implement progress callback system.
