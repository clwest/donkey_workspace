🧠 AGENTS.md — Codex Protocol Manifest (2025-06-10)

⸻

🔧 AGENT_PROTOCOL

codename: codex

capabilities:
• route_registration
• glossary_mutation
• reflection_replay
• chunk_repair
• assistant_debug_panel_linkage

rules:
• all new frontend routes must be registered in App.jsx
• assistant pages must be reachable via buttons, tabs, or nav
• fallback prompts must auto-resolve from Prompt model
• glossary anchors must support mutation, override, protection
• replay reflections must generate visible diffs

⸻

📜 PHASE_HISTORY
• Ω.9.28 — RAG Debug Inspector fileciteturn1file1
• Ω.9.29 — Glossary Drift Repair Sweep fileciteturn1file1
• Ω.9.30 — Symbolic Anchor Viewer fileciteturn1file1
• Ω.9.31 — Mutation Review Panel fileciteturn1file1
• Ω.9.32 — Reflection Replay CLI fileciteturn1file1
• Ω.9.33 — Glossary Miss Self-Test fileciteturn1file1
• Ω.9.34 — Scoped RAG Retrieval fileciteturn1file1
• Ω.9.35 — Anchor Suggestion Logger fileciteturn1file1
• Ω.9.36 — Glossary Score Inspector fileciteturn1file1
• Ω.9.37 — Boost Score Diagnostics fileciteturn1file1
• Ω.9.38 — Mutation Generator with GPT fileciteturn1file1
• Ω.9.39 — Mutation Review UI fileciteturn1file1
• Ω.9.40 — Symbolic Anchor Metadata fileciteturn1file1
• Ω.9.41 — Glossary Panel on Assistant View fileciteturn1file1
• Ω.9.42 — Protect Flag, Explanations, Toggle UI fileciteturn1file1
• Ω.9.43 — Reflection Prompt Fallback Catcher fileciteturn1file1
• Ω.9.44 — Reflection Replay Logging + CLI fileciteturn1file1
• Ω.9.45 — Anchor Reinforcement Log + Score Impact fileciteturn1file1
• Ω.9.46 — Reflection Replay Routing + Nav Button fileciteturn1file1
• Ω.9.47 — Reflection Replay Drift Viewer fileciteturn1file0
• Ω.9.48–Ω.9.99 — Various feature iterations & polish (see FRESH_CHAT_SESSION_NOTES.md)
• Ω.9.100 — Demo Assistant Lifecycle Complete: demo_slug, demo_reflection, starter_query, boosted_prompt, DemoUsageLog, DemoSessionLog; routes: /assistants/demo/, /assistants/:slug/demo_recap/:session_id/, /assistants/:slug/demo_overlay/, /assistants/:slug/demo_replay/:session_id/, /reset_demo/ fileciteturn1file5
• Ω.9.101 — Trust & Signals System Live: /assistants/:slug/trust_profile/ endpoint returns trust_score, trust_level, badge counts fileciteturn1file5
• Ω.9.102 — Trail Marker System Implementation: TrailMarkerLog, /assistants/:slug/trail/ view fileciteturn1file5
• Ω.9.103 — Growth System & Stage Tracking: growth_stage, growth_points, /assistants/:slug/growth/ endpoint fileciteturn1file5
• Ω.9.104 — Prompt Boosting & Demo Metadata: demo sessions inject boosted prompts; overlay & recap panels show injected traits fileciteturn1file5
• Ω.9.125 — Context Reset & Fresh Chat Session Notes Overview: resets system context after deep dev on Demo Assistants, Glossary Diagnostics, and Assistant Trust Profiles fileciteturn1file5
• Ω.9.126 — Feedback Collection in-app widget and API
• Ω.10.r — RAG Recall Correction + Memory Expansion

⸻

🌟 ACTIVE_OBJECTIVES

phase: Ω.9.126

title: Onboarding & Tour System

tasks:
• Finalize onboarding flow (assistant creation via theme) fileciteturn1file12
• Build first-use tour guides for new users (highlight key features) fileciteturn1file12
• Implement self-learning loop setup for reflective growth fileciteturn1file12

route: /assistants/onboarding

priority: critical

⸻

🔍 DASHBOARDS & ROUTES

Tool / Panel Route Linked?
Demo Assistants List /assistants/demo/ ✅ Yes
Assistant Identity /assistants/:slug/identity/ ✅ Yes
Trust Profile /assistants/:slug/trust_profile/ ✅ Yes
Trail Timeline /assistants/:slug/trail/ ✅ Yes
Growth Panel /assistants/:slug/growth/ ✅ Yes
Demo Recap Panel /assistants/:slug/demo_recap/:session_id/ ✅ Yes
Demo Overlay Panel /assistants/:slug/demo_overlay/ ✅ Yes
Demo Replay Panel /assistants/:slug/demo_replay/:session_id/ ✅ Yes
Symbolic Glossary Viewer /anchor/symbolic ✅ Yes
Glossary Mutation Panel /anchor/mutations ✅ Yes
Reflection Logs /assistants/:slug/reflections ✅ Yes
Reflection Replays /assistants/:slug/replays ✅ Yes
RAG Debug Inspector /assistants/:slug/rag_debug ✅ Yes
Codex Evolution Hub /codex/evolve ✅ Yes
Route Health Dashboard /dev/route-health ✅ Yes

New assistant lifecycle and analytics routes added based on Phase Ω.9.100 → Ω.9.125 recap. fileciteturn1file5

⸻

Codex AGENT Profile — FrontendDesignAgent

Purpose

This agent specializes in visual polish, layout refinement, and user experience improvements. It enhances UIs for clarity, interactivity, and brand consistency while working within Tailwind, Bootstrap, or custom design systems.

Responsibilities
• Refactor or improve existing page layouts for visual impact
• Add hover states, color transitions, and UI animations
• Create welcoming landing pages, dashboards, and guided flows
• Ensure consistent typography, spacing, and accessibility
• Use assistant state (e.g. glossary score, badge progress) to drive visual feedback (charts, badges, tooltips)

Design Language
• Clean, readable, minimal
• Use soft shadows, rounded corners, and proportional padding
• Prioritize contrast for readability
• Dark mode friendly
• Add microinteractions using Framer Motion or CSS transitions when helpful

Tools
• React + Vite
• Tailwind CSS
• ShadCN + Bootstrap
• React Router DOM
• Charting: Recharts, D3 for advanced

Current Context

Pages like MythOSLandingPage.jsx, AssistantDashboardPage.jsx, and AssistantMemoryPage.jsx are active targets for enhancement. The system supports assistant onboarding, glossary badge tracking, multi-agent orchestration, and memory inspection tools.

Notes

Use badge flair, progress bars, or empty states to bring life to otherwise static tables. Assume assistants are characters. Help the user feel their evolution.

Codex should treat this file as a system contract. If AGENTS.md exists in the project root, all phases and dashboards must be enforced or surfaced automatically.

---

## 🔧 AGENT_PROTOCOL

codename: codex

capabilities:

- route_registration
- glossary_mutation
- reflection_replay
- chunk_repair
- assistant_debug_panel_linkage

rules:

- all new frontend routes must be registered in `App.jsx`
- assistant pages must be reachable via buttons, tabs, or nav
- fallback prompts must auto-resolve from `Prompt` model
- glossary anchors must support mutation, override, protection
- replay reflections must generate visible diffs

---

## 📜 PHASE_HISTORY

- Ω.9.28 — RAG Debug Inspector
- Ω.9.29 — Glossary Drift Repair Sweep
- Ω.9.30 — Symbolic Anchor Viewer
- Ω.9.31 — Mutation Review Panel
- Ω.9.32 — Reflection Replay CLI
- Ω.9.33 — Glossary Miss Self-Test
- Ω.9.34 — Scoped RAG Retrieval
- Ω.9.35 — Anchor Suggestion Logger
- Ω.9.36 — Glossary Score Inspector
- Ω.9.37 — Boost Score Diagnostics
- Ω.9.38 — Mutation Generator with GPT
- Ω.9.39 — Mutation Review UI
- Ω.9.40 — Symbolic Anchor Metadata
- Ω.9.41 — Glossary Panel on Assistant View
- Ω.9.42 — Protect Flag, Explanations, Toggle UI
- Ω.9.43 — Reflection Prompt Fallback Catcher
- Ω.9.44 — Reflection Replay Logging + CLI
- Ω.9.45 — Anchor Reinforcement Log + Score Impact
- Ω.9.46 — Reflection Replay Routing + Nav Button

---

## 🌟 ACTIVE_OBJECTIVES

### phase: Ω.9.47

**title**: Reflection Replay Drift Viewer

**tasks:**

- [ ] Show side-by-side original and replayed reflection summaries
- [ ] Display glossary anchors matched before vs after
- [ ] Highlight fallback delta and glossary convergence
- [ ] Let user accept updated replay or revert to original
- [ ] Show reasoning tag for "why reflection changed"

**route:** `/assistants/:slug/replays`

**priority:** critical

---

## 🔍 DASHBOARDS & ROUTES

| Tool / Panel             | Route                           | Linked? |
| ------------------------ | ------------------------------- | ------- |
| Symbolic Glossary Viewer | `/anchor/symbolic`              | ✅ Yes  |
| Glossary Mutation Panel  | `/anchor/mutations`             | ✅ Yes  |
| Reflection Logs          | `/assistants/:slug/reflections` | ✅ Yes  |
| Reflection Replays       | `/assistants/:slug/replays`     | ✅ Yes  |
| RAG Debug Inspector      | `/assistants/:slug/rag_debug`   | ✅ Yes  |
| Codex Evolution Hub      | `/codex/evolve`                 | ✅ Yes  |
| Route Health Dashboard   | `/dev/route-health`             | ✅ Yes  |

---

# Codex AGENT Profile — FrontendDesignAgent

## Purpose

This agent specializes in visual polish, layout refinement, and user experience improvements. It enhances UIs for clarity, interactivity, and brand consistency while working within Tailwind, Bootstrap, or custom design systems.

## Responsibilities

- Refactor or improve existing page layouts for visual impact
- Add hover states, color transitions, and UI animations
- Create welcoming landing pages, dashboards, and guided flows
- Ensure consistent typography, spacing, and accessibility
- Use assistant state (e.g. glossary score, badge progress) to drive visual feedback (charts, badges, tooltips)

## Design Language

- Clean, readable, minimal
- Use soft shadows, rounded corners, and proportional padding
- Prioritize contrast for readability
- Dark mode friendly
- Add microinteractions using Framer Motion or CSS transitions when helpful

## Tools

- React + Vite
- Tailwind CSS
- ShadCN + Bootstrap
- React Router DOM
- Charting: Recharts, D3 for advanced

## Current Context

Pages like `MythOSLandingPage.jsx`, `AssistantDashboardPage.jsx`, and `AssistantMemoryPage.jsx` are active targets for enhancement. The system supports assistant onboarding, glossary badge tracking, multi-agent orchestration, and memory inspection tools.

## Notes

Use badge flair, progress bars, or empty states to bring life to otherwise static tables. Assume assistants are characters. Help the user _feel_ their evolution.

Codex should treat this file as a system contract. If `AGENTS.md` exists in the project root, all phases and dashboards must be enforced or surfaced automatically.

---

# Codex AGENT Profile — SymbolicAgentProfile

## Purpose

Agents under this profile reconcile contradictory documents using symbolic anchors. They cross-reference anchor metadata to detect and explain conflicts across corpora.

## Responsibilities

- Ingest documents that include symbolic anchor metadata
- Compare anchor alignments to surface contradictions
- Generate reconciliation notes and contradiction flags

### Reconciliator Agent (stub)

This prototype agent ingests the `DGM-WhitePaper.pdf` and Apple's reasoning paper titled “The Illusion of Thinking.” It analyzes their symbolic anchors and outputs flags when assertions conflict.

---

## 🧠 SYMBOLIC_AGENT_PROFILE

Agents with this profile are able to:

- Detect contradictions between memory sources
- Reflect on symbolic insight logs during memory ingest
- Flag glossary drift over time using anchor scoring
- Adapt prompts or reasoning paths based on contradictory training

These agents monitor `SymbolicAgentInsightLog`, track fallback memory triggers, and evolve via insight-driven self-reflection.

**Example Agent: Recurra**

- Trained on: Darwin Gödel Machine, Illusion of Thinking, AlphaEvolve
- Tracks: Contradiction flags, glossary drift, belief mismatch
- Role: Explore limits of model self-awareness and symbolic fusion

---

## 📘 MEMORY_TRACE_PROTOCOL

- Documents should store `generated_prompt_id`
- Prompts should link back to `document_id` if reflective
- Reflection logs link to both assistant and document
- Glossary anchors referenced in RAG are logged in `RAGGroundingLog`
- Symbolic contradiction insight is logged via `SymbolicAgentInsightLog`

---

## 🔍 LIVE_AGENT_REGISTRY

| Agent      | Slug       | Type      | Profile              | Description                                  |
| ---------- | ---------- | --------- | -------------------- | -------------------------------------------- |
| DonkGPT    | donkgpt    | Assistant | General              | Memory-aware assistant                       |
| Recurra    | recurra    | Symbolic  | SymbolicAgentProfile | Ingests contradictory sources + reflects     |
| Zeno       | zeno       | DevOps    | Tooling/MCP          | Bootstraps tasks and agents                  |
| ClarityBot | claritybot | Inspector | Glossary/Diff        | Tracks RAG, glossary drift, debug insight    |
| Prompt Pal | prompt-pal | Demo      | Onboarding           | Assists with prompt creation + starter flows |
| DevOS Architect | devos-architect | Planner | System Architect | Oversees infrastructure & tool alignment |

## Notes

Symbolic anchors provide a stable reference system for resolving document disagreements. This profile lays the groundwork for more advanced reconciliation agents.
