 # mcp_core App Model Overview

 This document walks through each Django model in `mcp_core/models.py`, shows how they relate, and points out gaps or improvement ideas.

 ---

 ## 1. MemoryContext

 Purpose: Stores contextual memory entries for agents, tasks, plans, projects, or other targets.

 Fields:
 - `target_type` (CharField): Type of entity the memory relates to (choices: agent, task, plan, project, other).
 - `target_id` (CharField): Identifier of the related record, stored as text for flexibility.
 - `content` (TextField): The memory content or description.
 - `important` (BooleanField): Marks high-priority memories.
 - `category` (CharField): Optional classification label.
 - `tags` (JSONField): List of arbitrary tags.
 - `created_at` (DateTimeField): Timestamp of creation.

 Relations:
 - Referenced by `Plan.memory_context` (FK).
 - Many-to-many linked from `ReflectionLog.related_memories`.

 Notes & Improvements:
 - Consider using `ContentType`/`GenericForeignKey` for stronger referential integrity.
 - Add indexes on `(target_type, target_id)` for faster lookups.
 - Normalize tag storage or switch to M2M for tag entities.

 ---

 ## 2. Plan

 Purpose: Defines a plan of action with optional linkage to a memory context.

 Fields:
 - `title` (CharField): Plan title.
 - `description` (TextField): Detailed description.
 - `memory_context` (ForeignKey → MemoryContext): Optional seed memory.
 - `created_by` (ForeignKey → User): Creator of the plan.
 - `created_at` (DateTimeField): Timestamp of creation.

 Relations:
 - One-to-many → `Task` via `Task.plan`.

 Notes & Improvements:
 - Add status or progress tracking fields.
 - Link to a formal `Project` model instead of free-text project names in `Task`.
 - Include `updated_at` and `updated_by` for audit trails.

 ---

 ## 3. Task

 Purpose: Tracks individual work items, optionally under a plan or project.

 Fields:
 - `title`, `description` (TextField).
 - `status` (CharField): Choice of open, in_progress, completed, blocked.
 - `plan` (ForeignKey → Plan): Optional grouping.
 - `project` (CharField): Free-text project identifier (simplified).
 - `assigned_to` (ForeignKey → Agent): Responsible agent.
 - `created_at` (DateTimeField), `due_date` (DateTimeField).

 Notes & Improvements:
 - Replace `project` text field with FK to a `Project` model.
 - Add priority, estimated effort, and ordering.
 - Index `status`, `assigned_to`, and `due_date` for performance.

 ---

 ## 4. Agent

 Purpose: Represents a human or AI actor participating in tasks and plans.

 Fields:
 - `name` (CharField), `agent_type` (CharField: human or ai).
 - `specialty` (CharField): Optional domain expertise.
 - `metadata` (JSONField): Arbitrary agent data.
 - `created_at` (DateTimeField).

 Relations:
 - One-to-many → `AgentThoughtLog` via `thoughts`.
 - ForeignKey reference in `Task.assigned_to` and `ActionLog.related_agent`.

 Notes & Improvements:
 - Extend with status (active/inactive) and contact info for humans.
 - Add indexing on `agent_type` or specialty.

 ---

 ## 5. AgentThoughtLog

 Purpose: Records sequential thoughts or chain-of-thought for an agent.

 Fields:
 - `id` (UUIDField): Primary key.
 - `agent` (ForeignKey → Agent).
 - `thought` (TextField), `thought_trace` (TextField): Optional detailed trace.
 - `created_at` (DateTimeField).

 Meta:
 - `ordering`: Newest first (`-created_at`).

 Notes & Improvements:
 - Link thoughts to contexts (e.g., `MemoryContext`) for richer history.
 - Add a `type` or `stage` field to classify thought purpose.

 ---

 ## 6. Fault

 Purpose: Captures defects or issues discovered in a task.

 Fields:
 - `task` (ForeignKey → Task).
 - `description` (TextField).
 - `status` (CharField): open or fixed.
 - `created_at` (DateTimeField).

 Notes & Improvements:
 - Include severity or priority levels.
 - Allow assignment to an agent or owner.

 ---

 ## 7. ReflectionLog

 Purpose: Logs reflective insights and summaries of past activities.

 Fields:
 - `title` (CharField): Short descriptor.
 - `raw_summary` (TextField): Bullet-point or memory dump.
 - `llm_summary` (TextField): LLM-generated detailed reflection.
 - `summary` (TextField): Concise summary or blurb.
 - `important` (BooleanField): Flag for priority reflections.
 - `related_memories` (ManyToMany → MemoryContext).
 - `tags` (ArrayField of CharField).
 - `mood` (CharField), `created_at` (DateTimeField).

 Notes & Improvements:
 - Normalize tags into a dedicated model or use JSON.
 - Add `created_by` to track the author of the reflection.

 ---

 ## 8. ActionLog

 Purpose: Chronicles CRUD and other actions taken on plans, tasks, or agents.

 Fields:
 - `action_type` (CharField): E.g., create, update, delete, assign, complete, reflect.
 - `description` (TextField).
 - `performed_by` (ForeignKey → User).
 - `related_agent` (ForeignKey), `related_task` (ForeignKey), `related_plan` (ForeignKey): Optional links.
 - `created_at` (DateTimeField).

 Notes & Improvements:
 - Add generic linking (ContentType) for broader coverage.
 - Include previous and new values for audit diff.

 ---

 ## 9. PromptUsageLog

 Purpose: Records each LLM or prompt-based operation for analytics and auditing.

 Fields:
 - `prompt_slug`, `prompt_title` (CharField).
 - `used_by` (CharField): Context of use (e.g., assistant reply, image gen).
 - `assistant_id`, `project_id` (UUIDField).
 - `input_context`, `rendered_prompt`, `result_output` (TextField).
 - `created_by` (ForeignKey → User), `created_at` (DateTimeField).
 - `prompt_id` (UUIDField), `purpose` (CharField), `context_id` (CharField), `extra_data` (JSONField).

 Meta:
 - `ordering`: Newest first (`-created_at`).
 - Indexes on `prompt_slug` and `used_by`.

 Notes & Improvements:
 - Include performance metrics (duration, tokens used).
 - Link to specific content via GenericForeignKey for traceability.

 ---

 # Cross-Model Connections & Gaps

 - **Memory & Reflection**: `MemoryContext` seeds `Plan` and enriches `ReflectionLog`.
 - **Plan/Task Hierarchy**: `Plan` groups `Task`, but `Task.project` is a free-text field.
 - **Agent Interactions**: `AgentThoughtLog` and `ActionLog` capture different facets of agent behavior.
 - **Prompt Auditing**: `PromptUsageLog` centralizes prompt operations across assistants and services.
 - **Tagging Patterns**: Mix of JSONField, ArrayField, and free-text tags; consider standardization.

 # Summary of Recommended Improvements

 1. Adopt `ContentType`/`GenericForeignKey` for flexible cross-model linking.
 2. Replace free-text `Task.project` with FK to a `Project` model.
 3. Unify tagging strategy (dedicated `Tag` model vs. JSON/Array fields).
 4. Enhance audit fields (`created_by`, `updated_at`, change diffs) across logs.
 5. Index high-traffic fields (`target_type`/`target_id`, `status`, `assigned_to`).
 6. Introduce status and versioning for `Plan` and `Agent` entities.
 7. Consolidate similar log models (`AgentThoughtLog`, `ActionLog`) into a generic event store if beneficial.