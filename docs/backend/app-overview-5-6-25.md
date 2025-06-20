# 🧠 Donkey AI Assistant – Codex Project Checklist

> Project status as of May 6, 2025  
> This checklist tracks what's done, what's in progress, and what's next for assistant features, prompt flows, and memory wiring.

---

## ✅ Prompt Management

- [x] Load `prompt_sets/` into database — Completed 2025-05-18
- [x] Display prompts in frontend (Prompt Explorer) — Completed 2025-05-18
- [x] AI-powered prompt generation from idea input — Completed 2025-05-18
- [x] Prompt mutation tools (clarify, expand, casual, etc.) — Completed 2025-05-18

- [ ] Assign prompt to assistant (via dropdown or prompt link)
- [ ] Live preview of assigned system prompt
- [ ] Support prompt versioning / mutation history
- [ ] Allow rollback / compare of prompt versions

---

## ✅ Assistant System

- [x] View list of assistants (demo + user-created) — Completed 2025-05-18
- [x] Create new assistant (name, tone, specialty, model) — Completed 2025-05-18
- [x] View thought log (basic working) — Completed 2025-05-18
- [x] View memory logs (raw display) — Completed 2025-05-18
- [x] View session history (structured) — Completed 2025-05-18

- [ ] Assign prompt to assistant (see above)
- [ ] Show live preview of system prompt
- [ ] Improve thought log formatting (markdown, timestamps, AI feedback)
- [ ] Add feedback buttons (👍 / 👎) per message
- [ ] Link memories to assistant
- [ ] Show filtered memories per assistant
- [ ] Reflection summary panel (optional stretch)

---

## ✅ Memory System

- [x] Memory saves from chat sessions — Completed 2025-05-18
- [x] Transcripts + tags + embeddings are stored — Completed 2025-05-18
- [x] Tags inferred via OpenAI + saved to DB — Completed 2025-05-18
- [x] Memory list view in frontend — Completed 2025-05-18

- [ ] Link `MemoryEntry.assistant` on save
- [ ] Enable filtering by assistant on memory view
- [ ] Add topic filter or tag search
- [ ] Show memory relevance or importance sorting

---

## ✅ Projects

- [x] Create new projects — Completed 2025-05-18
- [x] View project detail page — Completed 2025-05-18

- [ ] Edit project name / desc / goals
- [ ] Assign assistant to project
- [ ] Add objectives, progress fields
- [ ] Wire objectives into assistant workflows

---

## 🌱 Future Stretch Goals

- [ ] Mutation version graph view
- [ ] Assistant recommendation engine
- [ ] Prompt auto-testing sandbox
- [ ] Auto-reflection agent summaries
- [ ] Assistant-level analytics dashboards
- [ ] Codex-style agent to monitor & refactor this system

---

_This checklist should evolve with the system — keep adding and checking items as the assistant grows._
