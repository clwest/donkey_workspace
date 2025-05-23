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
| `/codex` | `MythOSCodexPage` | Codex interaction layer |
| `/dream` | `DreamframePage` | Playback symbolic dream footage |
| `/ritual` | `MythOSRitualsPage` | Launch available rituals |
| `/reflection` | `ReflectionPage` | Personal reflection console |
| `/ritual/rewards` | `RitualRewardsPage` | View symbolic earnings and claim incentives |
| `/assistants/:id/economy` | `AssistantEconomyPage` | Assistant codex alignment and belief productivity |
| `/guilds/:id/funding` | `GuildFundingPage` | Manage guild symbolic reserves and proposals |

✅ **Note:** All routes now follow the `/assistants/` prefix for clarity and consistency.

Let Chris know if any additional routes should be included or reorganized!

## 🔹 Phase X Symbolic Routes

| Path | Component | Purpose |
| ---- | --------- | ------- |
| `/assistants/:id/fork` | `AssistantForkPage` | Symbolic divergence viewer |
| `/assistants/:id/interface` | `AssistantInterfacePage` | Live assistant portal |
| `/assistants/:slug/thoughts` | `AssistantThoughtsPage` | Full thought logs |
| `/codex/converge` | `CodexConvergePage` | Codex convergence ceremonies |
| `/codex/proof` | `CodexProofPage` | Symbolic integrity viewer |
| `/ritual/containers` | `RitualContainersPage` | View persistent ritual containers |
| `/replay/engine` | `ReplayEnginePage` | Belief replay engine |
| `/dream/rebirth` | `DreamRebirthPage` | Trigger dream rebirth |
| `/anchor/continuity` | `ContinuityAnchorPage` | Symbolic continuity dashboard |
| `/guilds/council` | `ArbitrationCouncilPage` | Arbitration council UI |
| `/treaty/forge` | `TreatyForgePage` | Symbolic treaty creation interface |
| `/federation/codices` | `FederationCodicesPage` | Codex Federation dashboard |
| `/law/ritual` | `RitualLawPage` | Ritual law viewer |
| `/deploy/standards` | `DeployStandardsPage` | Belief-aligned environment evaluator |
| `/summon/federated` | `FederatedSummonPage` | Federated assistant summoner |
