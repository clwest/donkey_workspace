# Phase 13.3 — Dashboard Notifications, Codex State Alerts & Ritual Status Beacons

Phase 13.3 introduces live symbolic feedback through the MythOS assistant dashboard. It adds belief-aligned notifications, codex tension alerts and ritual status beacons that visually update with real-time insight.

## Core Components
- **AssistantNotificationPanel** – dashboard UI for codex updates, ritual readiness and memory triggers.
- **CodexStateAlertSystem** – evaluates codex entropy, belief coherence and assistant alignment drift.
- **RitualStatusBeaconBar** – displays ritual availability, cooldown and entropy-based glow.

## View Routes
- `/assistants/:id/interface` – mounts the notification panel and beacon bar.

## Testing Goals
- Alerts trigger when rituals become ready or codex mutation votes open.
- Codex state indicators reflect stress levels.
- Beacons change based on assistant directive and codex pull.
