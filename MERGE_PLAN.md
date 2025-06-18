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