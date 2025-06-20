📘 MODULE_ROADMAP.md — MindOS Module Overview & Purpose

🎯 Purpose

Provide architectural clarity across your Django apps by:
	•	Mapping core system responsibilities
	•	Highlighting key capabilities and data patterns (embeddings, RAG, reflection)
	•	Grouping related apps into feature clusters
	•	Guiding Codex to merge deeply by referencing module intent

⸻

🧩 Module Clusters & Descriptions

1. Memory & Embedding Stack
	•	intel_core / embedding_utils
→ Handles text chunking, embedding generation, and storage (PGVector).
Capability flags: embedding: true, vector fields present.
	•	memory
→ Stores semantic memory entries, history logs, and retrieval metadata.
	•	rag / retrieval modules
→ RAG orchestration, similarity search, query routing.

2. Reflection & Assistant Reasoning
	•	reflection_engine / assistant_thoughts
→ Manages user reflection prompts, drift detection, feedback loops.
	•	agents / assistant
→ Defines assistant workflows: assistant prompts, action chains, decision logic.
	•	prompts / prompt_usage_log
→ Tracks prompt templates, prompt mutations, and usage history.

3. Glossary & Anchoring
	•	glossary
→ Anchor definitions, glossary entries, concept linking for semantic memory.

4. Training & Workflow Tools
	•	training / insights
→ Collects training journeys, usage insights, model fine-tuning logs.
	•	tools
→ Utility scripts, ingestion pipelines, parsing routines.

⸻

🧠 Capability Matrix

Module
Embedding
Reflection
Glossary
RAG
Assistant
intel_core
✓
✓
memory
✓
reflection_engine
✓
✓
agents
✓
✓
prompts
✓
glossary
✓
tools
📦 Integration Suggestions
	•	Merge embedding & memory: Retain a unified MemoryEntry with semantic fields + vector embeddings.
	•	Unify assistant engines: Merge agents, reflection_engine, and prompts logic into a core assistant service.
	•	Centralize retrieval: Consolidate RAG modules under memory/retrieval.py.
	•	Glossary anchoring: Integrate glossary concept resolution into reflection chain backend.
	•	Strip training cruft: Archive or defer heavy training pipelines; focus on core runtime flows.

⸻

🚀 Structure Proposal
/backend/mindos_core/
    models.py        # MemoryEntry, PromptLog, ReflectionEntry, GlossaryAnchor
    views.py         # ThoughtEntrySet, AssistantActionSet, ReflectionTriggerView
    utils/
        retrieval.py
        embedding.py
        reflection.py
        glossary.py
/frontend/src/
    components/
        VoiceCapture/
        ThoughtTimeline/
        ReflectionPanel/
        AssistantConsole/
    hooks/
        useMemory(), useAssistant()
    utils/
        embedding.ts
        assistantClient.ts

📌 Instructions for Codex
	•	Preserve embeddings, RAG, reflection, and glossary logic, referencing this roadmap.
	•	Merge intelligently using capability overlaps — use model-field flags to detect vector fields.
	•	Remove duplicates, especially models like Thought vs MemoryEntry vs ReflectionLog.
	•	Reorganize into the structural outline provided, ensuring tests and docs follow.
	•	Maintain reflection + assistant loop flow as a core user journey.

⸻
