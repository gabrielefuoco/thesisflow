# Change: Modernize UX

## Why
Elevate the visual quality and user flow of ThesisFlow to provide a more premium, distraction-free academic writing environment.

## Context
- **Aesthetic**: The current UI uses standard CustomTkinter colors which feel functional but not particularly "premium" or modern compared to other academic tools (like Obsidian or Zettlr).
- **Navigation Context**: While writing in chapters or paragraphs, the user can lose track of the broader project context.
- **Workflow Friction**: Switching between Dashboard and Editor feels abrupt.

## What Changes
1. **Refined Design System**: Update `Theme` with a curated palette using HSL values for harmony, better contrast, and a modern "slate" aesthetic.
2. **Contextual awareness**: Introduce a `Breadcrumb` component in the editor header that displays `Project > Chapter [> Paragraph]`.
3. **Dashboard Polish**: Improve the "Workbench" feel of the dashboard with cleaner project cards and consistent spacing.
4. **Subtle Transitions**: Implement smoother view switching logic in the `ViewRouter`.

## Impact
- Affected specs: `theme-system`, `breadcrumb-nav`
- Affected code: `src/ui/theme.py`, `src/ui/app.py`, `src/ui/dashboard.py`

## Success Criteria
- The application UI feels cohesive and modern (verified by visual inspection).
- Navigation breadcrumbs accurately reflect the project hierarchy.
- Dark and Light modes both provide high legibility and aesthetic appeal.
- No regression in icon visibility or alignment.
