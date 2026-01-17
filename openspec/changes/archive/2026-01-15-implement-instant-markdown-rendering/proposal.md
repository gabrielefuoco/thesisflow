# Change: Implement Instant Markdown Rendering

## Why
Users currently have a split experience between a basic text editor and a separate preview panel. Modern markdown editors like Obsidian provide a "Live Preview" experience where the markdown syntax is elided and rendered in-place, reducing friction and making the writing process more intuitive and visually appealing.

## What Changes
- **Live Preview Editor**: The `EditorFrame` will now elide markdown syntax characters (`#`, `**`, `_`) and apply rich-text formatting (bold, italics, header sizing) directly within the `CTkTextbox` as the user types.
- **Context-Aware Elision**: Syntax markers will only be visible on the line where the cursor is currently active, allowing for easy editing while maintaining a clean "rendered" look elsewhere.
- **Optimized Preview Logic**: The secondary preview pane (if enabled) will be optimized for faster, flicker-free updates.

## Impact
- **Affected specs**: `markdown-rendering` (NEW)
- **Affected code**: `src/ui/editor.py`, `src/ui/theme.py`
