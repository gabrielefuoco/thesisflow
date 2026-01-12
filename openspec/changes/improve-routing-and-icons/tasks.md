# Tasks: Improve Routing and Icons

## Phase 1: Icon Fixes
- [ ] Update `generate_icons.py` with missing drawing functions. <!-- id: 0 -->
- [ ] Rerun `generate_icons.py` to populate `assets/icons/`. <!-- id: 1 -->
- [ ] Verify all UI buttons now display icons. <!-- id: 2 -->

## Phase 2: Centralized Routing
- [ ] Create `src/ui/router.py` with `ViewRouter` class. <!-- id: 3 -->
- [ ] Refactor `ThesisFlowApp` to use `ViewRouter` for view management. <!-- id: 4 -->
- [ ] Implement "Back" logic consistently across views. <!-- id: 5 -->

## Phase 3: Validation
- [ ] Run `openspec validate improve-routing-and-icons --strict`. <!-- id: 6 -->
- [ ] Manual test of all navigation flows. <!-- id: 7 -->
- [ ] Verify no console warnings for missing icons. <!-- id: 8 -->
