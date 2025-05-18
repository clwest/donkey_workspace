# Assistant API to Frontend Mapping

This document outlines the mapping between `/api/assistants/` backend endpoints and their corresponding frontend pages or components.

All API requests now require JWT authentication via an `Authorization: Bearer <token>` header.

---

## 🧠 Assistants Overview

| **Endpoint**                                  | **View Function**               | **Frontend Page**                      | **Notes**                          |
| --------------------------------------------- | ------------------------------- | -------------------------------------- | ---------------------------------- |
| `/api/assistants/`                            | `assistants_view`               | `/assistants/`                         | Assistant listing page             |
| `/api/assistants/create/`                     | `assistants_view` (POST)        | `/assistants/create`                   | Assistant creation form            |
| `/api/assistants/<slug:slug>/`                | `assistant_detail_view`         | `/assistants/[slug]`                   | Detail page for a single assistant |
| `/api/assistants/<slug:slug>/chat/`           | `chat_with_assistant_view`      | `/chat/[slug]`                         | Chat interface                     |
| `/api/assistants/<slug:slug>/think/`          | `think_with_assistant`          | `AssistantThinkButton`                 | Trigger LLM thought from assistant |
| `/api/assistants/<slug:slug>/submit-thought/` | `submit_assistant_thought`      | `ThoughtInput` component               | User-submitted thought             |
| `/api/assistants/<slug:slug>/reflect/`        | `reflect_on_assistant_thoughts` | Reflect button in `/assistants/[slug]` | Assistant self-reflection          |
| `/api/assistants/<slug:slug>/thoughts/`       | `assistant_thoughts_by_slug`    | `/assistants/[slug]/thoughts`          | Thought history log                |
| `/api/assistants/demos/`                      | `demo_assistant`                | `/assistants/demos`                    | Listing of demo assistants         |

---

## 📂 Assistant Projects

| **Endpoint**                                                    | **View Function**              | **Frontend Page**                    | **Notes**                        |
| --------------------------------------------------------------- | ------------------------------ | ------------------------------------ | -------------------------------- |
| `/api/assistants/projects/`                                     | `assistant_projects`           | `/assistants/projects`               | All assistant projects           |
| `/api/assistants/projects/<uuid:pk>/`                           | `assistant_project_detail`     | `/assistants/projects/[id]`          | Single project overview          |
| `/api/assistants/projects/<uuid:project_id>/thoughts/`          | `project_thoughts`             | `/assistants/projects/[id]/thoughts` | Thought log per project          |
| `/api/assistants/projects/<uuid:project_id>/thoughts/generate/` | `generate_assistant_thought`   | Generate button                      | Calls `AssistantThoughtEngine`   |
| `/api/assistants/projects/<uuid:project_id>/thoughts/reflect/`  | `reflect_on_thoughts`          | Reflect button                       | Project-level reflection         |
| `/api/assistants/projects/<uuid:pk>/ai_plan/`                   | `ai_plan_project`              | 🟡 TBD                               | AI-suggested project plan        |
| `/api/assistants/projects/<uuid:project_id>/tasks/`             | `assistant_project_tasks`      | `/assistants/projects/[id]/tasks`    | Task list and creation           |
| `/api/assistants/projects/<uuid:project_id>/milestones/`        | `assistant_project_milestones` | 🟡 TBD                               | Milestone planning UI            |
| `/api/assistants/projects/<uuid:project_id>/objectives/`        | `assistant_project_objectives` | 🟡 TBD                               | Might overlap with above         |
| `/api/assistants/projects/generate-mission/`                    | `generate_project_mission`     | POST-only                            | Mission statement autogeneration |
| `/api/assistants/projects/<uuid:project_id>/linked_memories/`   | `linked_memories`              | 🟡 TBD                               | Memory linking page              |
| `/api/assistants/projects/link_memory/`                         | `link_memory_to_project`       | POST-only                            | Memory link API                  |
| `/api/assistants/projects/<uuid:project_id>/linked_prompts/`    | `linked_prompts`               | 🟡 TBD                               | Show linked prompt chains        |
| `/api/assistants/projects/link_prompt/`                         | `link_prompt_to_project`       | POST-only                            | Prompt link API                  |

---

## 🧩 Assistant Utilities

| **Endpoint**                                              | **View Function**        | **Frontend Page** | **Notes**                    |
| --------------------------------------------------------- | ------------------------ | ----------------- | ---------------------------- |
| `/api/assistants/objectives/<uuid:objective_id>/actions/` | `assistant_next_actions` | 🟡 TBD            | Linked to planning UI        |
| `/api/assistants/signals/`                                | `signal_catches`         | 🟡 TBD            | Logging signal inputs        |
| `/api/assistants/signals/create/`                         | `create_signal_catch`    | POST-only         | Signal entry API             |
| `/api/assistants/signals/<uuid:pk>/`                      | `update_signal_catch`    | PATCH-only        | Edit individual signal entry |
| `/api/assistants/sources/`                                | `signal_sources`         | 🟡 TBD            | Manage signal sources        |

---

Let me know if you want this version pushed to `/docs/api-assistants.md` or paired with linkable routes inside the frontend too!
