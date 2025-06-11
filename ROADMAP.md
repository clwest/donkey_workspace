# 🛠️ MythOS Development Roadmap

This document outlines current, near-term, and future goals for the MythOS assistant system.

---

## 🔥 Current Priorities (June 2025)

- [x] Fix document ingest status feedback (`progress_error`)
- [x] Prevent empty reflections
- [x] Add fallback summary chunks when ingest fails
- [ ] Auto-link documents to `memory_context`
- [ ] Track `generated_prompt_id` for reflection UI
- [ ] Display linked prompts + memory in UI
- [ ] Surface symbolic insight logs in assistant views

---

## 🧠 Active Assistants

| Name       | Type      | Description                               |
| ---------- | --------- | ----------------------------------------- |
| DonkGPT    | General   | Memory-aware assistant                    |
| Recurra    | Symbolic  | Ingests contradictory sources + reflects  |
| Zeno       | DevOps    | Bootstraps tasks and tools, builds agents |
| ClarityBot | Inspector | Tracks RAG, glossary drift, debug info    |
| Prompt Pal | Demo      | Assists with prompt creation + onboarding |

---

## 🔬 Experiments in Progress

- ✅ The Trinity of Self (DGM + Apple + AlphaEvolve)
- 🧪 Self-doubt reflection loop
- 🧪 Memory-based prompt mutation tracking
- 🧪 Symbolic insight logs on ingest conflict

---

## 📅 Near-Term Goals

- Add assistant-specific memory panels (RAG debug, glossary, reflection replays)
- Create `/codex/evolve/` to track prompt & assistant mutations
- Add `anchor_retention_score` to glossary anchors
- Build glossary mutation review UI

---

## 🧗 Long-Term

- Memory-based assistant feedback loops
- Agent collaboration via narrative threads
- Self-training assistants with curriculum assignment
- Revenue experiment: tiered access to private agents + dashboards
