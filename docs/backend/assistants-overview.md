# Assistants App Model Overview

This document walks through each Django model in `assistants/models.py`, shows how they relate, and points out gaps or improvement ideas.

---

## 1. Assistant

**Purpose**: Core “agent” definition.
Fields:

- `id, slug, name, description, specialty`
- Config: `system_prompt (Prompt FK)`, `personality`, `tone`, `preferred_model`
- Runtime: `memory_mode`, `thinking_style`
- Status flags: `is_active`, `is_demo`

Relations:

- One-to-many → `AssistantThoughtLog` (`thoughts`)
- One-to-many → `Project` (`assistant`)
- Uses `Prompt` (via `system_prompt`)

Notes & Improvements:

- **Missing**: Link back to reflection logs?
- Enforce Prompt tag validation on `system_prompt`.
- Allow multiple prompts (history of templates) via M2M.

## 2. Project

**Purpose**: A multi-step “project” or context the assistant works on.
Fields:

- `title, description, goal, initial_prompt`
- Status: `status`
- Source: `created_from_memory (MemoryEntry FK)`

Relations:

- FK → `Assistant`
- FK → `MemoryEntry` (spawned from memory)
- One-to-many → `AssistantThoughtLog`, `AssistantReflectionLog`, `AssistantObjective`, `AssistantPromptLink`, `AssistantMemoryChain`, `ProjectTask`, `AssistantReflectionInsight`

Improvements:

- **Missing**: M2M to users/teams.
- `initial_prompt` → use `Prompt` FK for consistency.
- Add `due_date`, `owner`.

## 3. AssistantThoughtLog

**Purpose**: Records every “thought” (user input, chain-of-thought, planning, reflection).
Fields:

- `assistant` or `project` (one required)
- `thought_type` (choice), `thought`, `thought_trace`, `linked_memory (MemoryEntry FK)`

Relations:

- FK → Assistant or Project
- FK → MemoryEntry

Improvements:

- Enforce exclusive requirement via DB constraint (not just `clean()`).
- Index on `thought_type` + `created_at` for faster querying.
- Add sentiment or token count.

## 4. AssistantReflectionLog

**Purpose**: Summarizes and tags project-level reflections.
Fields:

- `project`, `title`, `mood`, `summary`, `llm_summary`, `insights`, `tags (PromptTag M2M)`

Relations:

- FK → Project
- M2M → `PromptTag` (via `prompts.PromptTag`)
- Related: `linked_memories` via reverse from MemoryEntry (seeded in migrations)

Improvements:

- Persist link to source memories (explicit M2M).
- Add `reflection_type` or `phase`.
- Better naming: `llm_summary` → `model_summary`.

## 5. AssistantObjective

**Purpose**: Tracks high-level objectives in a project.
Fields:

- `project` FK, `title`, `description`, `is_completed`

Relations:

- FK → Project
- One-to-many → `AssistantNextAction`

Improvements:

- Add ordering or priority.
- Tag M2M for categorization.

## 6. AssistantPromptLink

**Purpose**: Links a `Prompt` (from `prompts` app) into a project with rationale.
Fields:

- `project` FK, `prompt` FK, `reason`, `linked_at`

Relations:

- FK → Project
- FK → Prompt

Improvements:

- Enforce indexing on `(project, prompt)` (already unique).
- Support link “state” (active/archived).

## 7. AssistantMemoryChain

**Purpose**: Named chains of memories + prompts to drive structured recall.
Fields:

- `project` FK, `title`, `description`
- M2M → MemoryEntry
- M2M → Prompt

Relations:

- FK → Project
- M2M → MemoryEntry, Prompt

Improvements:

- Add ordering in the chain.
- Enforce min/max chain length.
- Better introspection API.

## 8. AssistantReflectionInsight

**Purpose**: Atomic insight items from reflections.
Fields:

- `project` FK, `content`, `created_at`

Relations:

- FK → Project

Improvements:

- Tagging (link to PromptTag or custom Label model).
- Categorize insight by theme.

## 9. AssistantNextAction

**Purpose**: Action items under an objective.
Fields:

- `objective` FK, `content`, `completed`, `created_at`

Relations:

- FK → AssistantObjective

Improvements:

- Add due dates, assigned-to.
- Migrate to generic Task model? (see `ProjectTask`)

## 10. ProjectTask

**Purpose**: Task list on a project (parallel to Objectives/NextActions).
Fields:

- `project` FK, `title`, `notes`, `content`, `status`, `priority`, `created_at`

Relations:

- FK → Project

Improvements:

- Deduplicate with Objective/NextAction or unify under a single `Task` model.
- Add `assigned_to` FK → User.
- Add `due_date`, `tags`, `attachments`.

---

# Cross-Model Connections & Gaps

- **Assistant ↔ Project**: Clear.
- **Thoughts ↔ Memories**: uses `linked_memory`. Could add M2M for multi-memory thoughts.
- **Reflections ↔ Memories**: currently via migration tagging; add explicit M2M.
- **Objectives ↔ Tasks**: duplicated semantics; consider consolidation.
- **Prompts integration**: unify `system_prompt` (Assistant) & `initial_prompt` (Project) under Prompt model.
- **User/Team ownership**: no links to Django `User` for auditing/ownership.
- **Signal-driven updates**: define Django signals to auto-create tasks when NextActions are added, etc.

# Summary of Recommended Improvements

1. Introduce ownership & user relationships across all models.
2. Consolidate Tasks, Objectives, NextActions into single `Task` model with hierarchy/labels.
3. Strengthen prompt usage by replacing free-text prompts (`initial_prompt`) with FK to `Prompt`.
4. Add explicit M2M relationships where implied (e.g. Reflection ↔ Memory).
5. Add audit fields (updated_at, updated_by) for traceability.
6. Index and constraint tuning for performance and data integrity.
