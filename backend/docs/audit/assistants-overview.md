# Assistants App Overview

## Core Models
- **Assistant**: Base configuration for an AI assistant. Links to `prompts.Prompt` as `system_prompt`. Can have `parent_assistant` and many `documents`.
- **AssistantThoughtLog**: Stores internal thoughts with embedding and optional linked memory.
- **AssistantProject**: Workspace per assistant with tasks, objectives, reflections.
- **AssistantTask** / **AssistantObjective** / **AssistantNextAction**: Task and goal tracking tied to a project.
- **AssistantReflectionLog**: Summary text produced during reflection cycles.
- **ChatSession**, **AssistantChatMessage**, **StructuredMemory**: Handle chat history and token usage.
- Additional models for memory chains, signal sources, topics and audio responses.

## Serializers
- `AssistantSerializer`, `AssistantProjectSerializer`, `AssistantThoughtLogSerializer`, and related serializers handle nested relations.

## Views & Endpoints
- `assistants_view` `/assistants/` for listing/creating assistants.
- `assistant_detail_view` `/assistants/<slug>/` returns a single assistant.
- `chat_with_assistant_view` `/assistants/<slug>/chat/` handles chat and memory creation.
- Multiple project endpoints (`/assistants/projects/`, `/projects/<id>/tasks/`, etc.).
- Thought and reflection endpoints under `/assistants/thoughts/` and `/assistants/<slug>/reflect/`.
- Session endpoints to list or flush chat sessions.

## Utilities
- `assistant_thought_engine.AssistantThoughtEngine` – generates and logs thoughts, runs reflection cycles.
- `assistant_session` – Redis backed session helper.
- `assistant_reflection_engine` – summarises memory contexts and generates structured reflections.
- `bootstrap_helpers.generate_objectives_from_prompt` – creates initial objectives from a prompt.

## Dependencies
- Heavy use of `memory` for `MemoryEntry` creation and linking.
- Embedding helpers from `embeddings` to store vectors.
- Links to `intel_core.Document` and `mcp_core` Tag and NarrativeThread models.
- Many views import `project` for linking to `Project` and `ProjectTask`.
