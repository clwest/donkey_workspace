🧠 AGENTS.md — Codex Protocol Manifest (2025-06-14)

⸻

🔧 AGENT_PROTOCOL

codename: codex

capabilities:
• route_registration
• glossary_mutation
• reflection_replay
• chunk_repair
• assistant_debug_panel_linkage
• anchor_suggestion
• mutation_scoring

rules:
• all new frontend routes must be registered in App.jsx
• assistant pages must be reachable via buttons, tabs, or nav
• fallback prompts must auto-resolve from Prompt model
• glossary anchors must support mutation, override, protection
• replay reflections must generate visible diffs
• mutation scores must track reinforcement outcomes across anchors

⸻

📜 PHASE_HISTORY
• Ω.9.28 — RAG Debug Inspector
• Ω.9.29 — Glossary Drift Repair Sweep
• Ω.9.30 — Symbolic Anchor Viewer
• Ω.9.31 — Mutation Review Panel
• Ω.9.32 — Reflection Replay CLI
• Ω.9.33 — Glossary Miss Self-Test
• Ω.9.34 — Scoped RAG Retrieval
• Ω.9.35 — Anchor Suggestion Logger
• Ω.9.36 — Glossary Score Inspector
• Ω.9.37 — Boost Score Diagnostics
• Ω.9.38 — Mutation Generator with GPT
• Ω.9.39 — Mutation Review UI
• Ω.9.40 — Symbolic Anchor Metadata
• Ω.9.41 — Glossary Panel on Assistant View
• Ω.9.42 — Protect Flag, Explanations, Toggle UI
• Ω.9.43 — Reflection Prompt Fallback Catcher
• Ω.9.44 — Reflection Replay Logging + CLI
• Ω.9.45 — Anchor Reinforcement Log + Score Impact
• Ω.9.46 — Reflection Replay Routing + Nav Button
• Ω.9.47 — Reflection Replay Drift Viewer
• Ω.9.48–Ω.9.99 — Various feature iterations & polish (see FRESH_CHAT_SESSION_NOTES.md)
• Ω.9.100 — Demo Assistant Lifecycle Complete
• Ω.9.125 — Context Reset & Fresh Chat Session Notes Overview
• Ω.10.r — RAG Recall Correction + Memory Expansion
• Ω.10.t — RAG Recall Booster
• Ω.10.u — Symbolic Feedback Review Panel
• Ω.10.v — RAG Diagnostic Export Patch
• Ω.10.w — Anchor Mutation Review Scoring: introduced mutation_score and reinforcement_log on symbolic anchors; CLI recomputes score deltas; frontend includes Mutation Scorecard tab and anchor history modal for trust analysis.

⸻

🌟 ACTIVE_OBJECTIVES

phase: Ω.10.w

title: Anchor Mutation Review Scoring

tasks:
• Recalculate scores from reinforcement logs
• View mutation_score in UI
• Review anchor trustworthiness before applying mutation
• Color-code results by confidence level

route: /anchor/suggestions → Mutation Scorecard

priority: high

⸻

🔍 DASHBOARDS & ROUTES

Tool / Panel Route Linked?
Mutation Scorecard /anchor/suggestions ✅ Yes
Anchor Suggestions /anchor/suggestions ✅ Yes
Symbolic Glossary Viewer /anchor/symbolic ✅ Yes
Glossary Mutation Panel /anchor/mutations ✅ Yes
Reflection Logs /assistants/:slug/reflections ✅ Yes
Reflection Replays /assistants/:slug/replays ✅ Yes
RAG Debug Inspector /assistants/:slug/rag_debug ✅ Yes
