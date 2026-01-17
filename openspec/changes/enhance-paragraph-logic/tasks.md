# Tasks: Enhance Paragraph Logic

- [x] **Infrastructure & Models**
    - [x] Update `Chapter` model to include `paragraphs` list in `src/engine/models.py`. <!-- id: 1 -->
    - [x] Update `ProjectManifest.to_dict` and `from_dict` to support nested paragraphs. <!-- id: 2 -->
    - [/] Add migration logic to `ProjectManager.load_project` to import existing sub-sections into the manifest. <!-- id: 3 -->

- [ ] **Paragraph Management Logic**
    - [ ] Implement `ProjectManager.create_paragraph(chapter, title)` and update `create_subsection` (deprecated). <!-- id: 4 -->
    - [ ] Implement `ProjectManager.delete_paragraph(chapter, paragraph)`. <!-- id: 5 -->
    - [ ] Implement `ProjectManager.move_paragraph(chapter, paragraph, direction)`. <!-- id: 6 -->

- [ ] **UI Enhancements**
    - [x] Update `SidebarFrame.update_chapters` to display numbered chapters (e.g., "1. Introduzione"). <!-- id: 7 -->
    - [x] Update `SidebarFrame.render_chapter_item` to display numbered paragraphs (e.g., "1.1 Sotto-sezione"). <!-- id: 8 -->
    - [/] Update `ThesisFlowApp.load_file` and `load_chapter` to show the full numbered path in the header. <!-- id: 9 -->

- [ ] **PDF Export Fix**
    - [ ] Update `ProjectManager.compile_project_async` to iterate over paragraphs and wrap them in Level 2 Typst headings. <!-- id: 10 -->
    - [ ] Update `master_default.typ` template to enable hierarchical numbering. <!-- id: 11 -->

- [ ] **Verification**
    - [ ] Run `pytest tests/test_models.py` and `tests/test_project_manager.py`. <!-- id: 12 -->
    - [ ] Manual verification: Create a chapter and 2 paragraphs, check GUI numbering. <!-- id: 13 -->
    - [ ] Manual verification: Export to PDF and check paragraph rendering and numbering. <!-- id: 14 -->
