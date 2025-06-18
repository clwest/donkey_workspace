MERGE_PLAN.md — MindOS System Consolidation Blueprint

## ✅ Core Modules to Keep
- `memory.models.MemoryEntry`
- `assistants.models.Assistant`
- `assistants.models.AssistantThoughtLog`
- `assistants.models.AssistantReflectionLog`
- `assistants.models.Project`
- React page routes like `AssistantThoughtLogPage` and `MemoryBrowserPage`

## 🔁 Merge Candidates
- `memory.MemoryFeedback` with feedback-style models across apps → unify as `ThoughtFeedback`
- Duplicate project/task models (`ProjectTask`, `AssistantObjective`, `AssistantNextAction`) → consolidate under a single Task model
- Multiple reflection-related utilities → centralize reflection engine

## ⚠️ Conflicts
- Overlapping prompt models across `prompts` and `assistants`
- Redundant Redis session helpers versus DB-backed sessions

## 🧱 Proposed Structure
/backend
    /mindos_core
        models.py
        views.py
        utils/
/frontend
    /components/ThoughtCapture/
    /components/Reflection/
    /pages/MemoryTimelinePage.jsx
    /pages/AssistantReflectionPage.jsx

## 🧠 Assistant-Sync Logic
- Saving a `MemoryEntry` triggers reflection via signal
- Assistant dashboard highlights recall status and drift

## 🚀 Phase 2 — Deep Module Merge
Phase 2 focuses on collapsing duplicate models and utilities across apps into a
single `mindos_core` service. Merge priorities derive from
`MODULE_ROADMAP.md` and `app_summaries_v2.json`:

- **Reasoning & Reflection**
  - Consolidate `assistant_thought_engine.py`, `thought_logger.py`, and various
    reflection helpers into `mindos_core/reflection.py`.
  - Keep `AssistantThoughtLog` and `AssistantReflectionLog` models; deprecate
    scattered replay utilities in favor of `ReflectionReplayLog`.
- **Memory & Embeddings**
  - Merge `MemoryEntry`, `MemoryFeedback`, and related feedback models into a
    unified `memory.py`. Preserve PGVector fields and embedding utilities from
    `embeddings/vector_utils.py`.
  - Ensure thought logs and anchor replay functions remain intact.
- **Glossary & RAG**
  - Combine glossary anchors with RAG retrieval logic under
    `mindos_core/retrieval.py`.
  - Maintain `RAGGroundingLog` and `AnchorReinforcementLog` for diagnostics.
- **Prompt & Planning Models**
  - Resolve duplicate prompt models by keeping those in `prompts/` and linking
    assistants directly via `PromptUsageLog`.
  - Collapse task generators (`task_generation.py`, `project_agent_helpers.py`)
    into a single planning module.

### Unified Structure Outline
```
/backend/mindos_core/
    __init__.py
    models/
        assistant.py        # Assistant, Task, PromptUsageLog
        memory.py           # MemoryEntry, ThoughtFeedback, anchors
        reflection.py       # Reflection logs and replay models
        embedding.py        # Embedding, TagConcept utilities
        retrieval.py        # RAG search + glossary integration
    utils/
        embedding_utils.py
        reflection_engine.py
        anchor_replay.py
        assistant_planner.py
        feedback.py
    views.py
    signals.py
/frontend/src/
    components/ThoughtCapture/
    components/Reflection/
    pages/MemoryTimelinePage.jsx
    pages/AssistantReflectionPage.jsx
```

This layout preserves PGVector linkages, Codex feedback routes, and existing
thought logs while removing redundant modules.
