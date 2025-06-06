# 🧠 AGENTS.md — Codex Protocol Manifest (2025-06-06)

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

Codex should treat this file as a system contract. If `AGENTS.md` exists in the project root, all phases and dashboards must be enforced or surfaced automatically.
