# Memory App Overview

## Core Models
- **MemoryEntry**: Primary memory record storing an event, transcript, tags, and links to projects, assistants, chat sessions and related objects via GFK.
- **MemoryChain**: Many-to-many grouping of memory entries.
- **MemoryFeedback**: User feedback or suggestions linked to a memory.
- **ReflectionFlag**: Flags a memory entry for risky content with severity and reason.

## Serializers
- `MemoryEntrySerializer` and `MemoryFeedbackSerializer` provide API representations.

## Views & Endpoints
- Endpoints for creating/listing memory chains and reflecting on memories (`/memory/reflect_on_memory/`).
- `memory_detail` CRUD for individual memory entries.
- Feedback endpoints to submit or list `MemoryFeedback`.

## Utilities
- `context_helpers.get_or_create_context_from_memory` builds `MemoryContext` objects for new memories.

## Dependencies
- Connects to `assistants` for chat sessions and thoughts, to `project.Project` via `related_project`, and to `intel_core.Document` for document references.
- Embeddings saved via `embeddings.helpers.helpers_io.save_embedding`.
