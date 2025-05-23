# 🧭 Assistant + Project Routes (Frontend)

This file documents all frontend route paths under `/assistants/`, their associated React components, and what they are used for.

---

## 🔹 Assistant Routes

| Path                     | Component                | Purpose                                  |
| ------------------------ | ------------------------ | ---------------------------------------- |
| `/assistants`            | `AssistantList`          | Lists all assistants                     |
| `/assistants/:slug/chat` | `ChatWithAssistantPage`  | Chat interface with a specific assistant |
| `/assistant-dashboard`   | `AssistantDashboardPage` | Overview dashboard of all assistants     |
| `/assistants/:id/rebirth` | `AssistantMythRebirthPage` | Assistant reincarnation portal |

## 🔹 Project Routes

| Path                                         | Component                     | Purpose                                          |
| -------------------------------------------- | ----------------------------- | ------------------------------------------------ |
| `/assistants/projects`                       | `ProjectsDashboardPage`       | Lists all assistant-linked projects              |
| `/assistants/projects/create`                | `CreateProjectPage`           | Full page project creation form                  |
| `/assistants/projects/create-from-memory`    | `ProjectCreateFromMemoryPage` | Creates a project by selecting existing memories |
| `/assistants/projects/:id`                   | `ProjectDetailPage`           | Detail view for one project                      |
| `/assistants/projects/:id/build`             | `ProjectTaskBuilderPage`      | Guided task builder                              |
| `/assistants/projects/:id/edit-tasks`        | `ProjectTaskEditor`           | Edit tasks manually                              |
| `/assistants/projects/:id/tasks`             | `ProjectTaskManagerPage`      | Task list manager with status updates            |
| `/assistants/projects/:id/status-board`      | `ProjectStatusBoardPage`      | Kanban-style overview                            |
| `/assistants/projects/:id/mission`           | `ProjectMissionBuilderPage`   | Auto-generate a project mission statement        |
| `/assistants/projects/:projectId/timeline`   | `ProjectTimelinePage`         | Timeline visualization                           |
| `/assistants/projects/:projectId/objectives` | `ProjectObjectivesPage`       | Objective breakdown                              |

## 🔹 Milestone Routes

| Path                                                           | Component             | Purpose                    |
| -------------------------------------------------------------- | --------------------- | -------------------------- |
| `/assistants/projects/:projectId/milestones`                   | `MilestonesPage`      | Milestone overview         |
| `/assistants/projects/:projectId/milestones/create`            | `MilestoneCreatePage` | Create a new milestone     |
| `/assistants/projects/:projectId/milestones/:milestoneId/edit` | `MilestoneEditPage`   | Edit an existing milestone |

---

## 🔹 MythOS Routes

| Path | Component | Purpose |
| ---- | --------- | ------- |
| `/timeline` | `WorldTimelinePage` | View global myth events |

✅ **Note:** All routes now follow the `/assistants/` prefix for clarity and consistency.

Let Chris know if any additional routes should be included or reorganized!
