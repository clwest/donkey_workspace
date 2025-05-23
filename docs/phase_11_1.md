# Phase 11.1 — Memory Navigator Timelines, Archetype Affinity Heatmaps & Belief Evolution Dashboards

Phase 11.1 adds live symbolic telemetry to the MythOS UI. Assistants can now visualize their memories, roles and beliefs as evolving datasets.

## Core Features

### MemoryNavigatorTimeline
```javascript
function MemoryNavigatorTimeline({ assistantId }) {
  // Displays memory events on a scrollable timeline.
}
```
Shows assistant memories along a zoomable timeline with filters for ritual tags.

### ArchetypeAffinityHeatmap
```javascript
function ArchetypeAffinityHeatmap({ assistantId }) {
  // Renders a grid of role alignment weights.
}
```
Visual heatmap of codex archetype affinity.

### BeliefEvolutionDashboard
```javascript
function BeliefEvolutionDashboard({ assistantId }) {
  // Charts belief signature drift and directive activity.
}
```
Tracks belief deltas and symbolic pressure over time.

## View Routes
- `/assistants/:id/timeline`
- `/assistants/:id/affinity`
- `/assistants/:id/belief`

## Testing Goals
- Memory events appear chronologically and filter by ritual tag
- Heatmaps update when archetype weights change
- Belief graphs react to codex edits and directive triggers
