# Design: UX Modernization

## Architecture

### 1. Theme System Refinement
The `Theme` class in `src/ui/theme.py` is the single source of truth for colors. We will move away from static hex codes to a more structured approach using HSL where possible, allowing for easier "variant" generation (e.g., hover states, border highlights).

**New Palette Structure:**
- **Slate Core**: Primary background and surface colors.
- **Teal Accent**: Refined teal for primary actions.
- **Translucency**: Use `rgba` or CTK's handling of transparency for panels to create a "layered" feel.

### 2. Breadcrumb Component
A new `Breadcrumb` widget will be added to `src/ui/components/`.
- **Purpose**: To provide hierarchical navigation context.
- **Implementation**: A horizontal frame of labels separated by ">" or "/" icons.
- **Integration**: The `ThesisFlowApp` will update the breadcrumb state whenever `load_chapter` or `load_paragraph` is called.

### 3. View Transitions
The `ViewRouter` will be slightly enhanced to support a simple "fade-in" effect by manipulating the `alpha` or `grid` visibility more deliberately, though Python's `tkinter` limits complex animations.

## Trade-offs
- **CustomTkinter Limitations**: We are constrained by CTK's widget set and performance. Complex shadows or blur (Acrylic/Mica) aren't natively supported on Windows without deep Win32 API calls, so we will focus on "pseudo-glass" effects using flat colors and precise borders.
- **Font Availability**: "Inter" is ideal but might not be on every user's system. We will specify a robust fallback stack.
