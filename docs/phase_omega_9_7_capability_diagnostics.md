# 🧠 Phase Ω.9.7 — Assistant Capability Audit & Diagnostics

This phase introduces backend utilities for mapping API routes to assistant capabilities and exposes diagnostics for each assistant.

## New Features

- **Route → View Mapping** `/api/dev/routes/fullmap/` now includes:
  - `view_name` and `module_path`
  - `capability` key if a route matches a registered capability
  - `connected` boolean flag
- **Capability Status Endpoint** `/api/capabilities/status/` accepts `?assistant=<slug>` and returns per-capability diagnostics:
  - `enabled` value from the assistant record
  - `connected` if the backend route exists
  - `last_called_at` timestamp from `CapabilityUsageLog`
- **Capability Usage Logging** helper `log_capability_usage()` and model `CapabilityUsageLog` track route invocations.

These tools make it easier to audit missing routes, confirm enabled features, and debug capability usage across assistants.
