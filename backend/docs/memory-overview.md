# Memory App Model Overview

This document walks through each Django model in `memory/models.py`, highlighting their purposes, fields, relations, and improvement suggestions.

---

## 1. MemoryEntry

**Purpose**: Captures discrete memory events or conversational logs with optional context and metadata.

**Fields**:

- `id` (UUIDField): Primary key.
- `timestamp` (DateTimeField): When the memory was recorded.
- `event` (TextField): Description of the memory or event.
- `emotion` (CharField): Optional emotion label (e.g., happy, sad).
- `importance` (IntegerField): Priority or salience (default 5).
- `related_project` (CharField): Free-text project identifier.
- `voice_clip` (FileField): Optional user-recorded audio clip.
- `chat_session` (ForeignKey → `assistants.ChatSession`): Link to chat session.
- `tags` (ArrayField of CharField): List of arbitrary tags.
- `is_conversation` (BooleanField): Marks conversational entries.
- `session_id` (CharField): Identifier for grouping memory entries.
- `full_transcript` (TextField): Complete transcript of the session.
- `linked_thought` (ForeignKey → `assistants.AssistantThoughtLog`): Associates with a thought log.
- `created_at` (DateTimeField): Record creation timestamp.

**Meta**:

- `ordering`: `-created_at` (newest first)

**Notes & Improvements**:

- Normalize `related_project` to FK rather than free-text.
- Index `timestamp`, `session_id`, and `importance` for efficient querying.
- Consider using `ContentType`/`GenericForeignKey` for flexible parent linking.
- Switch `tags` to a dedicated M2M `Tag` model for richer metadata.
- Add `created_by` field to track the author of the memory.
- Implement soft-delete or archival flags for memory lifecycle.

---

## 2. MemoryChain

**Purpose**: Groups sequenced `MemoryEntry` instances into named chains for structured recall.

**Fields**:

- `id` (UUIDField): Primary key.
- `title` (CharField): Human-readable name of the chain.
- `memories` (ManyToManyField → `MemoryEntry`): Ordered set of entries (ordering handled externally).
- `created_at` (DateTimeField): Timestamp of creation.

**Notes & Improvements**:

- Enforce explicit ordering (e.g., through a through-model with `order_index`).
- Add description or category for the chain.
- Link chains to projects or users for context.
- Track `created_by` and add `updated_at` for audit.

---

## 3. ReflectionLog

**Purpose**: Summarizes reflections over a time window, linking back to memories.

**Fields**:

- `id` (UUIDField): Primary key.
- `summary` (TextField): Reflective insights or analysis.
- `time_period_start`, `time_period_end` (DateTimeField): Window of reflection.
- `linked_memories` (ManyToManyField → `MemoryEntry`): Related memory entries.
- `created_at` (DateTimeField): Timestamp of creation.

**Notes & Improvements**:

- Add `title` or `insights` field for concise labeling.
- Include `created_by` to identify who authored the reflection.
- Normalize tags or categories for consistent filtering.
- Index on time window fields for range queries.

---

## 4. MemoryFeedback

**Purpose**: Allows users or agents to provide suggestions and rationale for `MemoryEntry` items.

**Fields**:

- `memory` (ForeignKey → `MemoryEntry`): Target memory entry.
- `project` (ForeignKey → `assistants.Project`): Optional project context.
- `thought_log` (ForeignKey → `assistants.AssistantThoughtLog`): Optional related thought.
- `context_hint` (TextField): Additional context for feedback.
- `suggestion` (TextField): Proposed edit or improvement.
- `explanation` (TextField): Rationale for the suggestion.
- `submitted_by` (ForeignKey → User): Author of the feedback.
- `created_at` (DateTimeField): Timestamp of submission.

**Notes & Improvements**:

- Add `status` (e.g., pending, accepted, rejected) for feedback lifecycle.
- Link feedback to a specific user session or event.
- Consider aggregating feedback into grouped discussions.
- Index on `memory` and `submitted_by` for rapid lookup.

---

# Cross-Model Connections & Gaps

- **assistants.ChatSession**: `MemoryEntry.chat_session` ties memory to interactive sessions.
- **Thought Integration**: `MemoryEntry.linked_thought` connects raw memories to thought logs.
- **Feedback Loop**: `MemoryFeedback` closes the loop between memories and assistant reflections.
- **Tagging Strategy**: ArrayField tags present; consider centralized tag management.
- **Ordering**: `MemoryChain` lacks explicit ordering metadata.

# Summary of Recommended Improvements

1.  Normalize free-text references (`related_project`) to proper FKs.
2.  Introduce audit fields (`created_by`, `updated_at`) across all models.
3.  Standardize tagging via a dedicated `Tag` model and M2M relationships.
4.  Enforce ordering in `MemoryChain` through a through-model with index.
5.  Add lifecycle and status fields to `ReflectionLog` and `MemoryFeedback`.
6.  Leverage `ContentType`/`GenericForeignKey` for flexible parent linking.
7.  Add appropriate indexes on timestamp, priority, and FK fields for performance.
