# Phase 13.02 — Directive Tracker, Identity Editor & Ritual Quick Actions Layer

Phase 13.02 enhances the assistant interface with dynamic tools for memory-driven growth. A live directive tracker displays belief goals and codex pressure, an identity card editor lets users adjust tone and traits, and a quick actions bar triggers rituals in real time.

## Core Components
- **DirectiveTrackerPanel** – shows active directive nodes with progress and codex pull.
- **IdentityCardEditor** – modal to edit assistant name, role tone and archetype traits.
- **RitualQuickActionsLayer** – bottom panel with buttons for Reflect, Recall, Rebirth and Anchor.

## View Routes
- `/assistants/:id/interface` – renders the directive tracker, mounts the quick actions bar and enables the identity editor modal.

## Testing Goals
- Directive panel updates with codex score and belief deltas.
- Identity editor saves tone and trait changes.
- Ritual buttons trigger the appropriate symbolic actions.
