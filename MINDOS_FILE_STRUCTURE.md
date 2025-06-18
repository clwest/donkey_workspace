# MindOS Unified File Structure (Phase 2)

This outline reflects the updated module layout once the Phase 2 merge is complete. It merges reasoning, memory, embeddings, glossary, RAG, and reflection logic into a single `mindos_core` package.

```
backend/
    mindos_core/
        __init__.py
        models/
            assistant.py        # core assistant + task models
            memory.py           # MemoryEntry, ThoughtFeedback, anchors
            reflection.py       # Reflection logs, replay, and diagnostics
            embedding.py        # Embedding & PGVector utilities
            retrieval.py        # RAG search and glossary usage
        utils/
            embedding_utils.py
            reflection_engine.py
            anchor_replay.py
            assistant_planner.py
            feedback.py
        views.py
        signals.py
frontend/src/
    components/ThoughtCapture/
    components/Reflection/
    pages/MemoryTimelinePage.jsx
    pages/AssistantReflectionPage.jsx
```

Supporting modules like `codex` feedback hooks, anchor replays, and PGVector linkages remain intact. Duplicate prompt and planning models across apps are removed in favor of the above unified files.

