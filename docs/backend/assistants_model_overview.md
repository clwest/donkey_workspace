# 🧠 Donkey AI — Assistants App Model Overview

| Model                          | Relationships                                                                                                                                          | Key Fields                                                            | Issues / TODOs                                                                                                | ✅  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --- |
| **Assistant**                  | FK → `Prompt` (`system_prompt`) <br> O2M → `Project`, `AssistantThoughtLog`                                                                            | `slug`, `name`, `specialty`, `memory_mode`, `preferred_model`, `tone` | ➕ Add user FK <br> 🧩 Support prompt history (M2M) <br> 🧪 Add system prompt tag validation                  | ⬜  |
| **Project**                    | FK → `Assistant`, `MemoryEntry` <br> O2M → `ThoughtLog`, `ReflectionLog`, `Objective`, `PromptLink`, `MemoryChain`, `ProjectTask`, `ReflectionInsight` | `title`, `goal`, `initial_prompt`, `status`                           | 🔄 Convert `initial_prompt` to FK → `Prompt` <br> ➕ Add `owner`, `due_date` <br> 👥 Add M2M for team members | ⬜  |
| **AssistantThoughtLog**        | FK → `Assistant` or `Project` <br> FK → `MemoryEntry`                                                                                                  | `thought`, `trace`, `thought_type`, `linked_memory`                   | 🔐 Require either `assistant` or `project` <br> 🧪 Add token count / sentiment <br> 🧩 M2M to `MemoryEntry`?  | ⬜  |
| **AssistantReflectionLog**     | FK → `Project` <br> M2M → `PromptTag`                                                                                                                  | `mood`, `summary`, `llm_summary`, `insights`, `tags`                  | ➕ Add `reflection_type` <br> 🧩 Add M2M to `MemoryEntry`                                                     | ⬜  |
| **AssistantObjective**         | FK → `Project` <br> O2M → `AssistantNextAction`                                                                                                        | `title`, `description`, `is_completed`                                | 🔀 Unify under `Task` model <br> 🏷️ Add tags or priority                                                      | ⬜  |
| **AssistantNextAction**        | FK → `AssistantObjective`                                                                                                                              | `content`, `completed`, `created_at`                                  | 🧩 Merge with `ProjectTask`/`Objective`                                                                       | ⬜  |
| **AssistantPromptLink**        | FK → `Project`, `Prompt`                                                                                                                               | `reason`, `linked_at`                                                 | 🧩 Add `status` (active/archived) <br> ➕ Add index (project, prompt)                                         | ⬜  |
| **AssistantMemoryChain**       | FK → `Project` <br> M2M → `MemoryEntry`, `Prompt`                                                                                                      | `title`, `description`                                                | 📏 Enforce ordering <br> 🔁 Standardize keying logic                                                          | ⬜  |
| **AssistantReflectionInsight** | FK → `Project`                                                                                                                                         | `content`, `created_at`                                               | 🏷️ Tag/category support                                                                                       | ⬜  |
| **ProjectTask**                | FK → `Project`                                                                                                                                         | `title`, `status`, `priority`, `content`                              | 🔁 Consolidate with `Objective`/`NextAction`                                                                  | ⬜  |

---

# ⚠️ Summary of Cross-Cutting TODOs

- 🔐 Add `user` FKs across all models for traceability
- 🔄 Consolidate `Objective`, `NextAction`, `Task` into one system
- 🧠 Migrate all prompt fields to use FK → `Prompt`
- 🧬 Index `thought_type`, `project`, and `prompt` fields for fast lookups
- 📡 Move LLM model/hyperparameters to centralized config (`llm_config.py`)
- 📝 Add consistent docstrings + type hints across helpers + utils
- ✅ Replace all unsafe eval/print/debug logic

---

# ✅ Status Legend

| Symbol | Meaning                      |
| ------ | ---------------------------- |
| ✅     | Fully implemented + reviewed |
| 🟡     | In progress                  |
| ⬜     | Not started                  |
| 🟥     | Known issue/blocker          |
