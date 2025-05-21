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

### ✅ Completed 3.0–3.32 Milestones

- ✅ Assistants linked to Projects, Objectives, and MemoryChains
- ✅ Assistant-to-Agent delegation chain with threading and context reuse
- ✅ Multi-assistant planning, thoughts-to-tasks, drift analysis
- ✅ Project planning timelines and session memory replay
- ✅ Feedback-based mutation, prompt refinement, and tone adjustment
- ✅ Dream Mode and speculative memory planning
- ✅ Reflection scoring, mood tagging, and assistant identity reconfirmation

---

## 🛠️ Phase 4: Tools, API Access, Agent Collaboration

### ✅ Phase 4.1–4.28 Completed

- ✅ Tool Registry with scoring, fallback, and execution routing
- ✅ Self-updating registry + tool usage feedback and prompt mutation
- ✅ Assistant-to-Assistant messaging + live relay support
- ✅ Emotional memory influence on task planning and delegation tone
- ✅ Team memory pools, delegation trust scores, and recovery workflows
- ✅ Assistant specialization drift detection and retraining suggestion
- ✅ Memory replay, bookmark, and recall from session context
- ✅ Identity self-assessment with dashboard logging
- ✅ `diff_knowledge` endpoint to compare assistant memory vs new input
- ✅ Recovery panel and misalignment status visualization

---

## 🧠 Current Focus: Phase 4.29–4.40 (Memory Linking, Narrative Threading, Visuals)

### ✅ Recently Completed

- ✅ Linked character, image, story, and video app endpoints from legacy Magical Mountains app
- ✅ Exposed `/api/images/`, `/api/characters/`, `/api/videos/`, `/api/story/`, `/api/tts/`
- ✅ Connected assistant → project → media asset pipelines
- ✅ Implemented context-aware memory chunk injection into assistant planning
- ✅ Chunk-level retry support and progress feedback from PDF ingestions
- ✅ Linking DevDocs and Videos to Assistants post-creation
- ✅ Memory visualizer in development: preparing chunk map, vector replay, timeline summaries

---

## 📌 TODO for Route & API Coverage

- [ ] ✅ Reconnect `/assistants/suggest/` and `/assistants/generate-mission/`
- [ ] ✅ Fix `/prompts/search/` endpoint or update frontend calls
- [ ] ✅ Enable council APIs `/assistants/council/` block
- [ ] ✅ Implement `/api/mcp/agent/<slug>/think/`
- [ ] ✅ Align `/api/projects/<uuid>` with frontend calls
- [ ] ✅ Map dashboard routes (slug-aware and primary-aware)
- [ ] ✅ Connect character/image/video frontend with linked assistant context

---

## 🎯 Next Up: Phase 4.29–4.40 Deep Narrative Linking

- 🧠 4.29: Memory Summarization + Feedback Tag Filters
- 🪄 4.30: Prompt Enhancement via Memory Review and Reuse
- 📚 4.31: Project Thread Rebuilding from Assistant Memory
- 🧵 4.32: Narrative-Based Delegation + Mood Replay
- 🕵️‍♂️ 4.33: Scene-Aware Memory Mapping
- 📽️ 4.34–4.36: Scene Replay, Agent Injection, Mood-Aware Planning
- 📈 4.37: Memory Bookmarking, Recall-on-Demand
- 🔁 4.38–4.41: Thread Reuse, Cross-Project Recall, Narrative Health Score

### 🆕 Phase 4.48: Mood Impact on Thread Continuity

- Capture assistant mood on thread creation
- Log mood snapshots with thoughts
- Diagnostics correlate mood volatility with plan drift
- Dashboard shows mood timelines next to thread health
- Celery task `analyze_mood_impact_on_thread_continuity` added

### 📝 Phase 4.52 Notes

- Enable assistants to detect when they’re drifting from a narrative thread and self-correct
- Auto-create thread summaries per project milestone

### 📝 Phase 4.54 Notes

- Enable agents to train new skills or fetch relevant documents based on feedback content

---

## ✅ Status

- Primary Assistant **DonkGPT** seeded and operational
- Codex handling backend & frontend flows via AGENTS.md guidance
- Assistants are reflecting, delegating, and now triggering tools + visual media
