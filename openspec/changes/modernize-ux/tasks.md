# Tasks: Modernize UX

- [/] 1. Core Theme Upgrade
    - [x] Update `src/ui/theme.py` with new palette and HSL logic.
    - [ ] Verify Light/Dark mode transitions.
- [x] 2. Breadcrumb Navigation
    - [x] Create `src/ui/components/breadcrumb.py`.
    - [x] Integrate `Breadcrumb` into `src/ui/app.py` header.
    - [x] Update breadcrumb logic in `load_chapter` and `load_paragraph`.
- [x] 3. Dashboard UI Refinement
    - [x] Redesign `ProjectCard` in `src/ui/dashboard.py`.
    - [x] Improve layout spacing and grid alignment.
- [x] 4. Visual Polish & Icons
    - [x] Update `ThesisFlowApp` global styles (rounded corners, spacing).
    - [x] Ensure all icons match the new theme's color intensity.
- [x] 5. Validation
    - [x] Verify all views look correct in both modes.
    - [x] Run `openspec validate modernize-ux`.
