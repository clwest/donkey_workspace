# Agents App Overview

## Core Models
- **Agent**: Represents an autonomous helper. Links to `assistants.Assistant` via `parent_assistant`. Stores preferred LLM and execution mode.
- **AgentThought**: Records an agent's thought with FK to `Agent` and optional reasoning/error fields.

## Serializers
- `AgentSerializer` exposes basic agent fields.

## Views & Endpoints
- `list_agents` – `/agents/` GET list.
- `agent_detail_view` – `/agents/<slug>/` GET single agent.

## Utilities
- `agent_controller.AgentController` – helper for creating reflections, plans and tasks, logging actions, and chatting with an agent.
- `agent_reflection_engine.AgentReflectionEngine` – summarizes important memories and analyzes mood.

## Dependencies
- Uses `mcp_core` models (`MemoryContext`, `Plan`, `Task`, `ActionLog`, `Tag`).
- Embedding functions from `embeddings.helpers` to persist vector data.
- Agents are seeded via management command `seed_agents` which relies on `assistants`.
