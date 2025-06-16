# Backend Subfolder Overview

This document maps out each top‑level backend subfolder in `backend/`, including purpose, current activity status, and recommendations.

---

## 📦 `assistants/`

- **Purpose**: Handles assistant models, chat sessions, memory, RAG diagnostics, and CLI tooling.
- **Status**: **Active** — core to application functionality.
- **Notes**: Contains related models, APIs, and frontend components.

---

## `embeddings/`

- **Purpose**: Manages text-to-vector operations, embedding metadata, repair/audit utilities.
- **Status**: **Active**
- **Notes**: Includes CLI commands for embedding repair and metadata fixes.

---

## `intel_core/`

- **Purpose**: Document ingestion, chunking, and RAG-related pipelines.
- **Status**: **Active**
- **Notes**: Includes chunk models, ingestion services, and debug endpoints.

---

## `mcp_core/dev_scripts/`

- **Purpose**: Contains diagnostic or seeding scripts for dev/prototyping.
- **Status**: **Dormant**
- **Recommendation**: Archive or remove once core ingestion scripts are solidified.

---

## `mcp_core/`

- **Purpose**: Memory context, narrative threads, plan/task utilities.
- **Status**: **Active**
- **Notes**: Key part of memory/multistep planning system.

---

## `memory/`

- **Purpose**: Stores MemoryEntry, chains, and chat memory models.
- **Status**: **Active**
- **Notes**: Tightly integrated with assistant recall and RAG.

---

## `project/`

- **Purpose**: Defines Projects, milestones, and project–assistant linkages.
- **Status**: **Active**
- **Notes**: Used for task/project workflows within assistants.

---

## `prompts/`

- **Purpose**: Handles prompt configurations, templates, and usage logs.
- **Status**: **Active**
- **Notes**: Includes system/configurable prompts for assistants.

---

## `tools/`

- **Purpose**: Manages tools, tool execution, and logs.
- **Status**: **Active**
- **Notes**: Tools UI and toolchain components tied to assistants.

---

## `images/`

- **Purpose**: Handles image generation and storage (in progress).
- **Status**: **In Progress / On Hold**
- **Notes**: Planned feature; not yet core.

---

## `story/`

- **Purpose**: Contains fictional/storytelling models, possibly for world‑building.
- **Status**: **Dormant / Low-Use**
- **Recommendation**: Either revive or remove if unused.

---

## `devtools/`, `analytics/`, `agents/`, etc.

- **Purpose**: Various debug panels, tooling, or experimental features.
- **Status**: **Needs Audit**
- **Recommendation**: Evaluate for active use or archive.

---

## 🛠️ Recommendations

1. **Archive or remove unused folders** (`story/`, `mcp_core/dev_scripts/`, etc.) once core functionality is stable.
2. **Consolidate experimental apps** into `devtools/` or `analytics/` with clear feature flags.
3. **Document ownership and dependencies** for each backend app in `README.md` or a root developer doc.
4. **Maintain this overview file**, updating it along with future app additions.

---

Generated on: **{{today}}**  
_(Update this document as apps evolve.)_
