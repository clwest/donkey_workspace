 # Prompts App Model Overview

 This document walks through each Django model in `prompts/models.py`, outlines their purposes, fields, relations, and suggests improvement ideas.

 ---

 ## 1. Prompt

 **Purpose**: Stores standardized system/user/assistant prompts for semantic search, retrieval, and reuse.

 **Fields**:
 - `id` (UUIDField): Primary key generated via `uuid.uuid4()`.
 - `title` (CharField[255]): Human-readable prompt title.
 - `slug` (SlugField, blank/null): URL-friendly identifier auto-generated from `title` and `id`.
 - `type` (CharField[50]): Prompt category (`system`, `user`, `assistant`).
 - `content` (TextField): The full prompt text.
 - `source` (CharField[255]): Origin or context of the prompt (e.g. seed file, user input).
 - `tags` (ManyToManyField → PromptTag): Semantic tags for organization.
 - `embedding` (VectorField[1536], null/blank): Optional vector for semantic similarity.
 - `complexity` (FloatField, null/blank): Computed complexity score.
 - `is_draft` (BooleanField): Draft flag to hide incomplete prompts.
 - `tone` (CharField[100], null/blank): Optional tone descriptor.
 - `token_count` (IntegerField): Precomputed token length.
 - `created_at`, `updated_at` (DateTimeField): Timestamps for record creation and updates.

 **Methods**:
 - `save()`: Ensures `slug` is generated from `title` and `id` if not provided.

 **Notes & Improvements**:
 - Add database index on `slug` and `type` for faster lookups.
 - Enforce unique constraint or handle collisions on `slug`.
 - Validate `content` length and optionally auto-compute `token_count` on save.
 - Trigger vector embedding updates automatically when `content` changes.

 ---

 ## 2. PromptTag

 **Purpose**: Defines tags for classifying and filtering prompts.

 **Fields**:
 - `id` (UUIDField): Primary key.
 - `name` (CharField[100], unique): Tag name.

 **Notes & Improvements**:
 - Add `description` or `category` field for richer tag metadata.
 - Track usage metrics (e.g., count of linked prompts).
 - Consider hierarchical tags or tag groups.

 ---

 ## 3. PromptPreferences

 **Purpose**: Stores per-user preferences affecting prompt handling and trimming.

 **Fields**:
 - `user` (OneToOneField → User): Owner of these preferences.
 - `auto_mode_enabled` (BooleanField): Flag for automated prompt selection.
 - `default_trim_threshold` (IntegerField, null/blank): Token threshold for trimming.
 - `excluded_sections` (ArrayField of Integers): Paragraph indexes to omit by default.
 - `updated_at` (DateTimeField): Timestamp of last update.

 **Notes & Improvements**:
 - Extend preferences to include default `tone`, `complexity` limits, etc.
 - Validate `excluded_sections` indexes against prompt length.
 - Add `created_at` or `last_accessed` for audit.

 ---

 ## 4. PromptUsageTemplate

 **Purpose**: Defines triggerable templates that link a `Prompt` to an `Assistant` with execution logic.

 **Fields**:
 - `title` (CharField[255]): Template name.
 - `description` (TextField): Optional details.
 - `prompt` (ForeignKey → Prompt): Underlying prompt.
 - `agent` (ForeignKey → assistants.Assistant): Target assistant.
 - `trigger_type` (CharField[50]): When to apply (`on_start`, `on_message`, `on_reflection`, `on_task`, `custom`).
 - `is_active` (BooleanField): Enable/disable flag.
 - `priority` (PositiveIntegerField): Execution order within an agent.
 - `fallback_text` (TextField, null/blank): Default text if prompt fails.
 - `created_at`, `updated_at` (DateTimeField): Timestamps.

 **Meta**:
 - `ordering`: by `agent`, `priority`, then `-created_at`.

 **Notes & Improvements**:
 - Index on `trigger_type`, `is_active`, and `priority` for efficient retrieval.
 - Support more granular trigger conditions (boolean expressions, schedules).
 - Consider `GenericForeignKey` for broader target types beyond assistants.
 - Add audit fields (`created_by`, `run_count`, `last_run_at`).

 ---

 # Cross-Model Connections & Gaps

 - **Assistant Integration**: `PromptUsageTemplate.agent` binds prompts to the `Assistant` model for automation.
 - **Embedding Pipeline**: Prompts store vector embeddings (`VectorField`); ensure embedding service handles this model.
 - **Tagging Consistency**: `PromptTag` is used in prompts; consider unifying with other tag models (e.g., `images.TagImage`).
 - **User Preferences**: `PromptPreferences` tailors prompt behavior; expand to cover more prompt-related settings.

 # Summary of Recommended Improvements

 1. Enforce unique and indexed slugs in `Prompt`.
 2. Automate embedding and complexity calculations on content change.
 3. Expand tag metadata and consider hierarchical tagging.
 4. Enrich `PromptPreferences` with more configurable options and audit trails.
 5. Enhance trigger logic in `PromptUsageTemplate` to support complex conditions and scheduling.
 6. Standardize tagging and embedding patterns across apps.