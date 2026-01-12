# Proposal: Improve Routing and Fix Icons

## Goal
Enhance the reliability and maintainability of the application's navigation system (routing) and ensure all UI icons are visible and representative of their actions.

## Problem
- **Icons**: Several icons used in the UI are missing from the `assets/icons` directory, leading to "invisible" buttons. Others are using generic placeholders.
- **Routing**: View management is currently manual and scattered across `app.py`, making it difficult to maintain state, handle transitions, or scale the application.

## Proposed Solution
1. **Centralized Routing**: Implement a `ViewRouter` to manage transitions between Dashboard, Editor, Bibliography, and Settings.
2. **Icon Refresh**: Update `generate_icons.py` to include missing icons and replace placeholders with unique, representative designs.

## Success Criteria
- No "Icon not found" warnings in the console.
- All toolbar and sidebar buttons display correct icons.
- Navigating between views is handled through a single point of control.
- Application state (like current project) is correctly preserved during transitions.
