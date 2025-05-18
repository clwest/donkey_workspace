# Donkey AI Assistant Integration Plan

This document outlines how the core apps link together to create an intelligent assistant with memory and reflection capabilities.

## Data Flow Overview

1. **Prompts → Assistants**
   - Prompts are stored via the `prompts` app. An assistant references a `Prompt` as its `system_prompt`.
   - Endpoint `/assistants/prompts/bootstrap-from-prompt/` uses `AssistantFromPromptSerializer` to create both an `Assistant` and an initial `AssistantProject` from a selected prompt.
   - `PromptUsageTemplate` records how prompts should be used during assistant actions.

2. **Assistants → Memory and Reflections**
   - Conversations through `/assistants/<slug>/chat/` generate `MemoryEntry` objects via `create_memory_from_chat`.
   - `AssistantThoughtEngine.log_thought` links each thought to a newly created memory entry and stores an embedding.
   - Reflection cycles (`/assistants/<slug>/reflect-now/`) read recent assistant memories and create `AssistantReflectionLog` records.

3. **Reflections Influence Projects and Objectives**
   - Each `AssistantProject` aggregates `AssistantObjective` and `AssistantNextAction` records.
   - Reflection summaries can be used to update project goals or create new tasks. (Future hook needed to auto-create objectives from reflection output.)
   - Project state is surfaced through the `project` app which also links related memories via `ProjectMemoryLink`.

4. **Intel Core and Embeddings Provide Context**
   - Documents ingested via `/intel_core/ingestions/` are saved as `intel_core.Document` with chunked embeddings.
   - `embeddings` app stores vectors for prompts, documents, thoughts and memories. Search APIs (`/embeddings/search/`) return similar content to enrich assistant responses.

5. **Memory Context Loop**
   - New `MemoryEntry` items call `get_or_create_context_from_memory` to create a `MemoryContext` in `mcp_core`, enabling cross-object grouping.
   - `AgentController.reflect` and `AssistantReflectionEngine.reflect_now` both write reflections into these contexts.

## Proposed Integration Enhancements

- **Signals**: Emit a signal when a `MemoryEntry` is created to automatically generate embeddings and tags instead of relying on Celery tasks.
- **Objective Updates**: After a reflection is saved, trigger creation of `AssistantObjective` or `ProjectTask` entries based on the reflection summary.
- **Search Hooks**: Expose helper to query `embeddings` for related documents whenever an assistant starts a chat session to preload context.
- **Consistency**: Unify serializers so `AgentSerializer` references `parent_assistant` (currently field mismatch) and ensure nested assistant/project endpoints share consistent slug/ID usage.

## Event Triggers

1. **Chat Message Saved** → create `MemoryEntry` → embedding & tag → update cached thoughts.
2. **Reflection Completed** → store `AssistantReflectionLog` → optional creation of objectives/tasks.
3. **Document Ingested** → generate embeddings → link to assistants or projects when relevant.

This integration plan ties together prompts, assistants, memory storage, reflection analysis, projects and document intelligence to form a cohesive assistant workflow.

## Connection Map

The diagram below summarises how the existing models interact.

- **prompts.Prompt** → referenced by **assistants.Assistant.system_prompt** and linked via **PromptUsageTemplate** for specific triggers.
- **assistants.Assistant** ↔ **assistants.AssistantProject** which groups tasks, objectives and reflection logs.
- **assistants.AssistantThoughtLog** → creates **memory.MemoryEntry** records; each entry has an **embeddings.Embedding** and optional **mcp_core.Tag**.
- **memory.MemoryEntry** links back to an **assistants.Assistant**, a **project.Project** via **ProjectMemoryLink**, and to documents through **intel_core.Document**.
- **intel_core.Document** is chunked into **DocumentChunk** objects; each chunk stores an **embeddings.Embedding** and can spawn a `MemoryEntry` for retrieval.
- **mcp_core.MemoryContext** groups related `MemoryEntry` items for reflection. `AssistantReflectionLog` writes summaries into these contexts.
- **embeddings.Embedding** uses a GenericForeignKey so prompts, thoughts, memories and document chunks all share the same search API.

This map highlights the feedback loops between chat messages, stored memories and project planning. New signals and tasks (see `tasks/todo_codex_integration.md`) will tighten these links further.
