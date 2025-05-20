# 🧠 AGENTS.md — Donkey Workspace AI Assistants

---

## ✅ Phase 2: Core Orchestration & Reflection

### Highlights Completed:

- ✅ Introduced `is_primary` flag to Assistant model
- ✅ Created `/assistants/primary/` endpoint and dashboard view
- ✅ Seeded **DonkGPT** as the primary orchestrator assistant
- ✅ Connected memory feed, reflection, and delegation log to Primary Assistant view
- ✅ Bootstrapped assistants from documents (assistant ↔ prompt ↔ document ↔ project)
- ✅ Added spawn agent buttons to memory entries
- ✅ Built out reflection + delegation endpoints and views
- ✅ Assistant detail views now show reflection, mood, thoughts, and memory

---

## 🚀 Phase 3: Contextual Memory, Task Planning & Project Linking

We are now in **Phase 3**, focused on deepening long-term memory, task planning, and assistant collaboration.

---

### 📌 Core Milestones Completed (Phase 3.0–3.32):

- ✅ Assistants linked to Projects + Objectives
- ✅ AssistantMemoryChain linked and editable with reflection filters
- ✅ Reflection reuse, feedback categorization, and prompt mutation
- ✅ Agents can spawn with inheritance of thread + memory context
- ✅ Hierarchical thought → project → milestone planning flow
- ✅ Delegation log, trust scores, and agent status summaries
- ✅ Multi-assistant project views with memory/role summaries
- ✅ Conversational session browser + replay
- ✅ Assistant mood tracking + tone-aware reflection
- ✅ Assistant personality and custom traits model
- ✅ Emotional memory mapping and mood-based planning shifts
- ✅ Thought-based objective generation and evolution
- ✅ Dream Mode: speculative planning thoughts

---

## 📋 Current Phase 3 Task Seeds (3.33 → 3.40)

These are active or queued for Codex tasks.

---

### 3.33: Agent Success Review + Task Reintegration

- Summarize completed agents and integrate memory into parent
- Reflect on completed delegation outcomes
- Link final output back to originating AssistantObjective

---

### 3.34: Memory Validation Interface

- Create UI for reviewing assistant memories
- Allow rating, editing, or flagging of memory events
- Support reflection reuse or suppression

---

### 3.35: Assistant Planning Timeline View

- Add Gantt-style or timeline view to ProjectDetailPage
- Display milestones, tasks, reflections, and assistant thoughts

---

### 3.36: Thought Tag Training + Context Embedding

- Train model on user-defined thought tags
- Suggest tags in UI based on recent entries
- Embed contextually tagged thoughts for rapid lookup

---

### 3.37: Reflection Reprioritization + Auto-Summarization

- Add endpoint to re-cluster and reprioritize recent reflections
- Auto-group related thoughts and prompt assistant to summarize
- Integrate with mood/memory tags for prioritization

---

## 🧭 Next Steps

- [ ] Open Codex tasks for 3.33–3.37
- [ ] Confirm frontend alignment with new data APIs
- [ ] Expand `AssistantPersonality`, `MoodEntry`, and `MemoryTrait` models
- [ ] Add `/docs/dev/phase3/*` overview + visuals

---
