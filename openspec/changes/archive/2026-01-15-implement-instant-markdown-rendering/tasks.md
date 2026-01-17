## [x] Implementation
- [x] Phase 1: Research & Theme Preparation
- [x] Phase 2: Editor Transformation
- [x] Phase 3: Preview Optimization
## 1. Research & Theme Preparation
- [x] 1.1 Add header font scale factors to `Theme` in `src/ui/theme.py`
- [x] 1.2 Verify `tk.Text` elide functionality in the current environment

## 2. Editor Transformation
- [x] 2.1 Update `setup_tags` in `src/ui/editor.py` to include `elide=True` for markdown markers
- [x] 2.2 Refactor `highlight_syntax` to handle elision-aware tagging
- [x] 2.3 Implement cursor-based "reveal" logic (reveal syntax on current line)
- [x] 2.4 Add support for eliding link syntax `[text](url)`

## 3. Preview Optimization
- [x] 3.1 Refactor `perform_updates` to reduce debounce time from 500ms to 100ms
- [/] 3.2 Optimize `render_markdown` to avoid full widget destruction when possible (partial updates)

## 4. Verification
- [ ] 4.1 Verify H1-H3 elision and styling
- [ ] 4.2 Verify Bold/Italic elision and styling
- [ ] 4.3 Verify stable cursor position and behavior when interacting with elided text
- [ ] 4.4 Run `openspec validate implement-instant-markdown-rendering --strict`
