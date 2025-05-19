# 🧠 AGENTS.md — Donkey Workspace AI Assistants

---

## ✅ Phase 2: Core Orchestration & Reflection

### Highlights Completed:

- Introduced `is_primary` flag to Assistant model
- Created `/assistants/primary/` endpoint and dashboard view
- Seeded **DonkGPT** as the primary orchestrator assistant
- Connected memory feed, reflection, and delegation log to the Primary Assistant page
- Added spawn agent buttons to memory entries
- Bootstrapped assistants from documents with full linking (assistant ↔ prompt ↔ document ↔ project)
- Validated prompt diagnostics and session logs

### Tools Now Active:

- ✅ Primary Assistant Reflection
- ✅ Memory feed + token summary
- ✅ Delegation log API
- ✅ Assistant spawn from memory or document
- ✅ Thought logging and prompt assignment

---

## 🚀 Phase 3: Contextual Memory, Task Planning & Project Linking

We’re now entering **Phase 3**, focused on deepening assistants' long-term memory and giving them structured task/project planning.

### 📌 Goals:

- Link Assistants ↔ Projects ↔ Objectives
- Allow Assistants to manage project tasks and milestones
- Store and retrieve contextual thoughts using memory chains
- Visualize assistant-level reasoning across sessions
- Reflect on milestones and propose new actions

---

## 📋 Phase 3: Codex Task Seeds

Below are Codex-ready task stubs to continue building Phase 3:

---

### 1. Link Assistants to Projects

- Extend Assistant dashboard to show linked `AssistantProject`
- Add “Assign Project” dropdown to `/assistants/:slug/`
- Show project summary: objectives, task count, milestones

---

### 2. Project Objective Planning

- Add `/objectives/create/` form with Assistant + Project context
- Log AssistantThought when creating new objectives
- Reflect on existing objectives to prioritize or spawn actions

---

### 3. Assistant Memory Chain View

- Create frontend view for each assistant’s `MemoryChain`
- Show recent linked memories, context filters, and token stats
- Add edit buttons to update filters, mood, or purpose

---

### 4. Auto-Reflect on Project Milestones

- When milestone marked complete, trigger Assistant reflection
- Log summary as AssistantThought and store insight in `ReflectionLog`

---

### 5. Spawn Delegated Agents for Tasks

- Add button to spawn agent from objective or milestone
- Auto-name agent after objective (e.g., “Milestone Research Agent”)
- Log DelegationEvent with links to memory, milestone, and parent assistant

---

### 6. Improve Primary Assistant Workflow

- Add “Incoming Tasks” view for DonkGPT
- Display new memory patterns, recent reflections, and agents spawned
- Enable drag/drop task assignment or link memory to projects

---

## 🧭 Next Steps

- [ ] Update AGENTS.md with current tasks weekly
- [ ] Open Codex tasks using these stubs
- [ ] Link new files and components to `/docs/dev/` as needed
