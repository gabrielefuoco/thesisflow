# Proposal: Improve Dynamic HTML Rendering

## Goal
Enhance the live preview capabilities of ThesisFlow by replacing the current rudimentary widget-based "mock" rendering with a robust, CSS-stylable HTML rendering engine.

## Context
Currently, `EditorFrame.render_markdown` manually parses a few markdown tokens and wraps them in standard `CTkLabel` widgets. This approach:
1. Is extremely limited (no tables, no nested lists, no inline styling in preview).
2. Is difficult to maintain and extend.
3. Doesn't feel like a "modern" writing experience.

## Proposed Solution
Introduce a proper Markdown to HTML conversion pipeline and use a dedicated HTML rendering widget in the preview pane.

### Architectural Changes
- **Converter:** Use `markdown2` or `mistune` for fast, extensible markdown parsing.
- **Renderer:** Use `tkhtmlview` (or `tkinterweb` for full CSS support) to display the resulting HTML.
- **Theming:** Inject a custom CSS stylesheet into the rendered HTML to ensure it matches the application's theme (Dark/Light mode).

## Benefits
- Support for 100% of CommonMark/GitHub Flavored Markdown.
- Consistent rendering between the preview and the final PDF export (via shared styles).
- Easier implementation of future features like mathematical formulas (KaTeX/MathJax).
