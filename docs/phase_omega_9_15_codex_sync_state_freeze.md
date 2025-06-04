# 🧠 Phase Ω.9.15 — Codex Sync + Assistant State Freeze

This phase introduces backend tools to verify assistant health, generate route diagnostics, and export snapshots for local backups. It acts as a stabilization checkpoint before the upcoming planning features.

## Checklist Overview

- **Codex Job Sync** – ensure all pending jobs are merged and update `/api/dev/routes/fullmap/` with `view`, `module`, and `name` fields.
- **Prompt Assignments** – confirm each assistant has a `system_prompt` and a recent source document.
- **Boot Diagnostics** – run `/api/assistants/self_tests/run_all/` and log results to `AssistantBootLog`.
- **Capability Coverage Diff** – compare `/api/capabilities/status/` against `/api/dev/routes/fullmap/` to mark missing or failing routes.
- **System Snapshots** – dev endpoints now return JSON dumps:
  - `/api/dev/export/assistants/`
  - `/api/dev/export/routes/`
  - `/api/dev/export/templates/`
- **UI Fixes** – wire up "Reflect Again" and "Repair Documents" buttons with proper POST calls.

When these checks pass, the platform enters a stable, reflection-ready state for Phase Ω.9.16.
