# Prompts App Overview

## Core Models
- **Prompt**: Stored prompt text with metadata, tags and optional embedding. Can reference a parent for remixes.
- **PromptPreferences**: User specific settings for auto mode and trimming.
- **PromptUsageTemplate**: Associates an `Assistant` with a prompt for a specific trigger type.

## Serializers
- `PromptSerializer` (includes tags and first assistant using the prompt).
- `PromptPreferencesSerializer`, `PromptCreateSerializer`, `PromptAssignAssistantSerializer`, `PromptUsageTemplateSerializer`.

## Views & Endpoints
- `list_prompts` `/prompts/` with optional search via embedding similarity.
- `create_prompt`, `prompt_detail`, `update_prompt` for CRUD.
- Generation endpoints: `generate_prompt_from_idea`, `reduce_prompt`, `auto_reduce_prompt_view`.
- Preference endpoints for the current user.

## Utilities
- `embeddings.get_prompt_embedding` computes vectors for prompts.
- `token_helpers` for counting and splitting tokens.
- `auto_reduce` and `mutation` for editing prompts via LLMs.
- `openai_utils.generate_prompt_from_idea` used in generation endpoint.

## Dependencies
- Links to `assistants` when assigning prompts as system prompts.
- Uses tagging from `mcp_core` and embeddings for search.
