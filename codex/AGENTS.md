
# 🧠 AGENTS.md — Donkey Workspace Codex System Guide

> Updated: 2025-06-04  
> Phase: Ω.9.25 Complete — Moving into Ω.9.26: System Sync & Memory UI Polish

---

## 🔁 Codex Integration Philosophy

Codex is your co-pilot — it writes, audits, routes, tests, reflects, and syncs the frontend/backend state. Its job is to follow **clear protocols** and **phase guides** to complete feature cycles **without dangling endpoints or unlinked UIs**.

All Codex tasks should conform to the following expectations:

- ✅ Routes must be visible in `/dev/route-health`
- ✅ Routes must have a `name` and linkable `view/module`
- ✅ Routes must be **discoverable** from the frontend (`App.jsx`, navbars, dashboards)
- ✅ Any assistant action (reflect, ingest, delegate) must be loggable, testable, and navigable
- ✅ If a feature has UI components, it must be **connected** to the app via buttons, tabs, or navigation links

---

## 🗂️ Project Components

- **Assistants** – persistent agents with memory, projects, and reasoning tools
- **Prompts** – reusable templates with tones, tokens, embeddings
- **Memory** – full transcript logging, memory chains, reflection summaries
- **Intel** – document ingestion, smart chunking, glossary tagging, and RAG vector search
- **Projects** – goals, tasks, milestones, delegation chains
- **Codex** – the active dev agent performing tests, patching routes, building dashboards

---

## ✅ Completed Phases (Highlights)

- Ω.9.6.b: Context Sync Enforcement + Reflection Fixes
- Ω.9.10: Clean Memory, Stale Projects, Repair Contexts
- Ω.9.15: Codex Sync + Assistant State Freeze + Capability Diagnostic
- Ω.9.16: RAG Repair + Prompt Reload Enforcement
- Ω.9.17: Memory + Embedding Link Audit
- Ω.9.19: Delegation Trace Routing + Reflection Diagnostics
- Ω.9.20: Reflection Summary Enrichment + Delegation Scope Tags
- Ω.9.21: Delegation Summary Engine + Transcript Sync
- Ω.9.22: Self-Reflection/Delegation Summary API + Route Registration
- Ω.9.25: Route Inspector + App.jsx Link Auditor

---

## 🔎 Active UI Dashboards

| Tool                        | Route                     | Linked? |
|----------------------------|---------------------------|---------|
| Route Health               | `/dev/route-health`       | ✅ Yes  |
| Route Explorer             | `/dev/route-explorer`     | ✅ Yes  |
| Assistant Boot Diagnostics | `/assistants/boot/`       | ✅ Yes  |
| Glossary Usage             | `/intel/glossary`         | ✅ Yes  |
| Template Drift             | `/dev/templates`          | ✅ Yes  |
| Delegation Summary Panel   | `/assistants/:slug/`      | ✅ Yes  |
| Sub-Agent Reflections      | `/subagent_reflect/:id/`  | 🟡 Manual only (link in delegation trace) |
| Self Reflection Trigger    | `/reflect_on_self/`       | ✅ Yes (via Assistant page) |
| Intel Debug Tools          | `/intel/debug/`           | ❌ Unlinked |
| Chunk Scores + Anchors     | `/intel/chunk-stats/`     | ✅ Yes |
| MythGraph + Simulation     | `/codex/strategy`         | ❌ Unlinked |
| All App.jsx Routes         | `/dev/app-routes`         | ✅ Yes (post Ω.9.25) |

---

## 🧩 Codex Protocol Reminders

1. **Every Route Must Be Registered**
   - All endpoints must be routed through `urls.py`, named, and visible in `/dev/route-health`.

2. **Frontend Links Required**
   - Every page in `App.jsx` must have a discoverable link in a navbar, dashboard, or dev panel.

3. **Reflective RAG Flow Must Trigger:**
   - After document ingest, `/assistants/:id/review-ingest/:doc_id/` should call:
     - `get_relevant_chunks()`
     - `reflect_on_document()`
     - `summarize_chunks_into_memory()`
     - optionally `build_agent_spawn_artifact()`

4. **Memory Validation**
   - Every `MemoryEntry` must have:
     - `assistant`, `context`
     - a non-empty `summary` or `full_transcript`
     - tagged anchor if glossary-linked
     - accurate timestamps and types (`reflection`, `delegation`, `conversation`, etc.)

5. **Glossary Anchors**
   - Chunks with `glossary_score = 0` must trigger glossary miss handling.
   - Anchor miss counts are visible in `/intel/glossary`.

---

## 📌 Next Suggested Phases

### Phase Ω.9.26 — System Sync & Memory UI Polish

- Fix sub-agent reflection buttons and route checks
- Add link from Assistant page to view full Delegation Summary
- Polish linked projects table (currently broken)
- Improve “Recent Memories” panel to filter/sort by type or importance
- Move Intel Debug Tools to sidebar or top nav
- Add Test Route buttons to `/dev/route-health`

---
