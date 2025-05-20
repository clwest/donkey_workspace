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

### ✅ Core Milestones Completed (Phase 3.0–3.32)

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

### 🔄 Phase 3.33–3.37 — In Progress / Queued

- [x] 3.33: Agent Success Review + Task Reintegration
- [x] 3.34: Memory Validation Interface
- [x] 3.35: Assistant Planning Timeline View
- [x] 3.36: Thought Tag Training + Context Embedding
- [x] 3.37: Reflection Reprioritization + Auto-Summarization

---

## 🛠️ Phase 4: Tools, API Access, and Execution Layer

### ✅ Completed through 4.24

- ✅ 4.1: Tool Registry Model + Execution Endpoint
- ✅ 4.2: Tool Invocation from Thought Context
- ✅ 4.3: Tool Reflection + Fallback Delegation Logic
- ✅ 4.4: Tool Scoring System + Context-Aware Selection
- ✅ 4.5: Self-Updating Tool Registry + Capability Awareness
- ✅ 4.6: Assistant Capability Profiles + Skill Graph
- ✅ 4.7: Delegation Routing via Capability Match
- ✅ 4.8: Tool-Enhanced Thought Generation + Planning Support
- ✅ 4.9: Assistant-to-Assistant Messaging + Live Relay Mode
- ✅ 4.10: Conversation Handoff + Agent Takeover
- ✅ 4.11: Routing Confidence Logs + Fallback Overrides
- ✅ 4.12: Assistant Routing Suggestions Based on Context & Tags
- ✅ 4.13: Assistant Routing History + Confidence Debugging Tools
- ✅ 4.14: Assistant Specialization Drift + Retraining Signal Detection
- ✅ 4.15: Self-Healing Assistants via Prompt Clarification + Reflection
- ✅ 4.16: Shared Assistant Memory Pools + Dynamic Linkage
- ✅ 4.17: Context-Aware Memory Retrieval and Prioritization
- ✅ 4.18: Dynamic Context Expansion via Related Memory & Mood
- ✅ 4.19: Multi-Agent Socratic Debugging Mode
- ✅ 4.20: Multi-Agent Debate + Consensus Building
- ✅ 4.21: Council Convene Protocol + Vote Handling
- ✅ 4.22: Emotional Resonance Logging + Assistant Empathy Tracing
- ✅ 4.23: Mood-Driven Collaboration Styles + Conflict Avoidance
- ✅ 4.24: Team Memory Chains + Assistant Roles in Shared Projects
- ✅ 4.28: Assistant Recovery Workflow (Drift Detection + Recovery Panel)

---

## ✅ Current Status

- Codex is actively iterating through Phase 4 features.
- Frontend and backend are linked and handling real assistant-to-agent flows.
- Primary assistant “DonkGPT” is now seeded, delegated, and operational.

---

## 🧭 Next Up (Phase 4.25+ Preview)

- 🧠 4.25: Persistent Assistant Personas + Custom Traits
- 🎭 4.26: Emotional Memory Mapping + Mood Influence
- 📈 4.27+: Dynamic Planning based on Mood, Memory, and Context
- 👁️‍🗨️ 4.29+: Memory Visualizer, Delegation Trace Views, Agent Feedback

### ✅ Phase 4.26: Assistant Knowledge Diffing + System Prompt Refinement

**Summary:**

- Added a new backend API endpoint: `/api/assistants/<slug>/diff-knowledge/`
- Enables comparing an assistant’s current prompt and memory state against new input text (e.g. updated documentation)
- Uses OpenAI to generate:
  - Suggested updates to system prompt
  - Tone/style alignment
  - Summary of knowledge gaps or contradictions

**Implementation:**

- `diff_knowledge()` view receives input text and assistant slug
- Retrieves assistant’s system prompt + recent memory entries
- Constructs a comparison prompt and submits to LLM
- Returns proposed refinements and tone suggestions

**Supporting Work:**

- Included tests covering:
  - Input validation
  - Successful diff and structured output
- Registered route and attached to assistant view module for use in frontend mutation workflows

**Next Steps:**

- Integrate with Assistant Prompt Edit UI for guided mutations
- Display suggested changes in `PromptRefinementPanel.jsx`
- Link this diff flow into the new **Assistant Recovery Workflow** (Phase 4.28)

### ✅ Phase 4.27: Assistant Identity Self-Assessment + Role Reconfirmation

**Summary:**

- Added new `thought_type="identity_reflection"` to `AssistantThoughtLog`
- Implemented `/api/assistants/<slug>/self_assess/` endpoint
  - Evaluates whether the assistant’s current behavior aligns with its defined tone, system prompt, and persona
  - Uses LLM to score tone, goal alignment, and recent behavior
- Results are saved as `AssistantThoughtLog` entries
- New modal `IdentityReflectionModal` displays this analysis in the dashboard
- Dashboard self-assessment trigger added to Primary Assistant panel

**Supporting Work:**

- Expanded API client and frontend hooks
- Added backend test verifying that self-assessment logs are stored properly

### ✅ Phase 4.28: Assistant Recovery Workflow for Misalignment or Memory Drift

**Summary:**

- Added `needs_recovery` boolean field to `Assistant` model
- Updated drift analysis (Phase 4.14) to mark assistants as needing recovery if drift threshold exceeded
- Introduced `requires_retraining` field in `SpecializationDriftLog` model
- Added `/api/assistants/<slug>/recover/` endpoint:
  - Generates a summary of the drift
  - Proposes edits to the assistant’s system prompt and personality
  - Logs a meta-thought entry
- Frontend Recovery Panel now displays when `needs_recovery` is true

**Visual Additions:**

- 🩹 "Misaligned" badge shown next to affected assistants
- Recovery action modal added to Primary Assistant dashboard

**Documentation:**

- Assistant Recovery section added to `AGENTS.md` including:
  - What triggers recovery
  - How to resolve
  - How logs are tracked
