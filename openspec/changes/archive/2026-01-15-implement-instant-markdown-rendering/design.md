## Context
The current editor is a plain `CTkTextbox` with basic regex-based syntax highlighting. The preview pane renders markdown into a series of `CTkLabel` widgets, which is slow for large documents and creates a disjointed experience.

## Goals
- Achieve an "Obsidian-style" Live Preview where the editor itself looks rendered.
- Support H1, H2, H3, Bold, and Italic elision.
- Maintain high performance during real-time typing.

## Decisions
- **Decision: Tag-based Elision**: Use Tkinter's native `tag_configure` with the `elide` attribute. This is efficient and supported by the underlying `tk.Text` widget.
- **Decision: Line-based Highlighting**: Update the syntax highlighting logic to be more performant by only re-evaluating the current and surrounding lines when possible, or using a very efficient full-scan for smaller documents.
- **Decision: Font Scaling**: Update `Theme` to provide scale factors for headers within the editor.

## Risks / Trade-offs
- **Risk**: Eliding text can sometimes make cursor placement confusing in Tkinter if not handled carefully (e.g., clicking on an elided region).
- **Mitigation**: Markers are revealed when the cursor enters the line.

## Open Questions
- Should we also elide link syntax `[text](url)`? (Proposed: Yes, ideally).
