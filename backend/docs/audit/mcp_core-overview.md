# MCP Core App Overview

## Core Models
- **MemoryContext**: Generic container for important memory text with GFK to any target object.
- **Plan**, **Task**, **Fault**, **ActionLog**: Basic planning and logging primitives.
- **PromptUsageLog**: Records when a prompt is rendered for a purpose.
- **Tag**: Global tagging model with optional embedding.
- **NarrativeThread**: Thread linking documents and memories to a theme.
- **DevDoc**: Internal documentation piece optionally linked to a `Document` and assistants.
- **GroupedDevDocReflection**: Captures grouped summaries across dev docs.

## Serializers
- Includes serializers for most models (e.g., `MemoryContextSerializer`, `PlanSerializer`, `DevDocSerializer`, `GroupedDevDocReflectionSerializer`, `NarrativeThreadSerializer`).

## Views & Endpoints
- Reflection endpoints under `/mcp_core/reflect/` and `/reflections/` for generating and expanding reflections.
- Prompt template CRUD and usage logging under `/mcp_core/prompt-usage/`.
- Dev doc endpoints: listing, reflecting, grouped summaries.
- Narrative thread endpoints for creating threads from memory and listing threads.

## Utilities
- `devdoc_reflection` – helper functions to reflect on DevDocs and group them.
- `auto_tag_from_embedding` and `tagging` – automatic tag generation.

## Dependencies
- Extensive relations to `assistants`, `memory`, `intel_core`, and `prompts` models.
- Utilizes embeddings for tagging and search.
