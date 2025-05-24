# Codex Integration TODOs

This list tracks glue code enhancements to better connect the core apps.

## Proposed Celery Tasks

- **reflect_on_project_memory(project_id)** – Run `AssistantReflectionEngine.reflect_now` when a new `ProjectMemoryLink` is created. Generates `AssistantReflectionLog` and `AssistantNextAction` items.
- **auto_tag_new_memory(memory_id)** – After a `MemoryEntry` is saved, compute embeddings and tags via `embeddings.helpers.helpers_io.save_embedding` and `mcp_core.tagging.auto_tag_from_embedding`.
- **bootstrap_assistant_from_doc(doc_id)** – When a new `intel_core.Document` is ingested, create a draft `Assistant` with `Prompt` generated from the document summary.
- **fragment_codex_clause(clause_id)** – Split a codex clause into fragments and log lineage to `FragmentTraceLog`.
- **decompose_ritual(ritual_id)** – Build a `RitualDecompositionPlan` and `DecomposedStepTrace` records.
- **mine_swarm_codification_patterns()** – Analyze prompt and ritual logs to create `SwarmCodificationPattern` entries and `CodexExpansionSuggestion` items.

## Signal Handlers

- `post_save` on `MemoryEntry` → trigger `auto_tag_new_memory` and link to any associated `Project`.
- `post_save` on `DocumentChunk` → create a `MemoryEntry` summarizing the chunk (see `docs/integration_recs.md`).
- `post_save` on `AssistantReflectionLog` → create `AssistantObjective` or `ProjectTask` from summary.

## API Endpoints

- `POST /assistants/<slug>/evolve/` – Generate new system prompt or objectives based on latest reflections.
- `POST /assistants/<slug>/tasks/auto/` – Auto-generate next actions from reflections and project state.
- `POST /projects/<uuid:pk>/memories/link/` – Attach existing `MemoryEntry` instances to a project.
- `GET /codex/fragment/<int:id>/` – Retrieve and edit clause fragments.
- `GET /ritual/decompose/<int:id>/` – View a ritual decomposition plan.
- `GET /codex/strategy/` – List swarm pattern suggestions for codex expansion.

These tasks will tighten feedback loops between assistants, memory, projects and documents.
