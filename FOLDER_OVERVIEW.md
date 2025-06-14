# Backend Folder Overview

This document summarizes the purpose and status of each top-level folder under `backend/`.

Legend:
- **Status**: `Active` (in regular use), `Partial` (incomplete or utility-only), `Unused` (appears obsolete)
- **Origin**: `User` (likely user-created) or `Codex` (added by Codex tasks)
- **Role**: high-level area such as Assistant Core, RAG, or DevTool
- **Notes** highlight missing files or unusual structure.

| 📁 Folder | ✅ Status | 🚩 Origin | 🧩 Role | 💬 Notes |
| --- | --- | --- | --- | --- |
| accounts | Active | User | Auth | Django app with models, views, and tests |
| agents | Active | Codex | Multi-agent orchestration | Full app: models, views, management |
| api | Partial | Codex | API helpers | Lacks `__init__`; utility modules only |
| assistants | Active | User | Assistant Core | Large app with models, views, tasks |
| backend | Partial | User | Utility Scripts | Contains `tools/` only |
| capabilities | Active | User | Capability registry | Django app with models and views |
| characters | Active | User | Character assets | Django app with tests |
| codex | Partial | Codex | Codex logic | Single module, not a full app |
| codex_tools | Partial | Codex | Codex helpers | Few scripts; no views |
| core | Partial | User | Service layer | Helper services, no models |
| devtools | Active | Codex | DevTool | Django app for dev dashboards |
| docs | Unused | User | Documentation | No code |
| documents | Partial | Codex | File API | Minimal views and urls |
| embeddings | Active | Codex | RAG & Embeddings | Models, tasks, and views |
| exports | Unused | User | Data exports | Markdown snapshots only |
| feedback | Active | Codex | Feedback API | Collects user feedback |
| images | Active | Codex | Image generation | Models and tasks |
| insights | Active | Codex | Analytics | Models and views |
| intel_core | Active | User | Document ingest | Models, processors, API routes |
| learning_loops | Active | Codex | Evaluation loops | Django app with tests |
| mcp_core | Active | User | Context protocol | Core orchestration models & views |
| memory | Active | User | Memory system | Full app with reflection helpers |
| memory_voices | Unused | User | Audio blobs | Contains single binary file |
| metrics | Active | Codex | Metrics & Prometheus | Django app with urls |
| mythcasting | Active | Codex | Narrative channels | Django app with tests |
| mythos | Partial | Codex | MythOS pages | Minimal views/urls |
| onboarding | Active | Codex | Onboarding flow | Config & views |
| overview_documents | Unused | User | Docs | Markdown overviews |
| pipelines | Partial | Codex | RAG pipelines | One script |
| project | Active | User | Project mgmt | Models and services |
| prompts | Active | User | Prompt store | Models and mutation logic |
| rag_debug | Partial | Codex | Debug scripts | Helper modules only |
| resources | Active | User | Resource API | Models and views |
| sandbox | Partial | Codex | Debug helpers | Not a formal app |
| scheduler | Partial | Codex | Scheduling | Only views folder |
| server | Active | User | Django project | Settings and root urls |
| simulation | Active | Codex | Simulation engine | Models, views, tests |
| static | Unused | User | Static data | JSON diagnostics |
| story | Active | User | Story models | App with tasks and services |
| storyboard | Active | Codex | Storyboard mgmt | Django app with controllers |
| tags | Partial | User | Tag model | Only models.py |
| tasks | Partial | Codex | Codex tasks | Views + TODO notes |
| tests | Partial | User | Test suite | Centralized tests, not an app |
| tools | Active | User | Tool registry | Models, services, and urls |
| trainers | Active | Codex | Training pipelines | Django app with tasks |
| tts | Active | Codex | Text-to-speech | Models, utils, tasks |
| utils | Partial | User | Shared utilities | Helper functions only |
| videos | Active | Codex | Video ingestion | Django app with tasks |
| workflows | Active | Codex | Workflow logs | Django app with urls |
