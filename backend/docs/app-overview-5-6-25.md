# 🧠 Donkey AI Assistant – Codex Project Checklist

> Project status as of May 6, 2025  
> This checklist tracks what's done, what's in progress, and what's next for assistant features, prompt flows, and memory wiring.

---

## ✅ Prompt Management

- [x] Load `prompt_sets/` into database
- [x] Display prompts in frontend (Prompt Explorer)
- [x] AI-powered prompt generation from idea input
- [x] Prompt mutation tools (clarify, expand, casual, etc.)

- [ ] Assign prompt to assistant (via dropdown or prompt link)
- [ ] Live preview of assigned system prompt
- [ ] Support prompt versioning / mutation history
- [ ] Allow rollback / compare of prompt versions

---

## ✅ Assistant System

- [x] View list of assistants (demo + user-created)
- [x] Create new assistant (name, tone, specialty, model)
- [x] View thought log (basic working)
- [x] View memory logs (raw display)
- [x] View session history (structured)

- [ ] Assign prompt to assistant (see above)
- [ ] Show live preview of system prompt
- [ ] Improve thought log formatting (markdown, timestamps, AI feedback)
- [ ] Add feedback buttons (👍 / 👎) per message
- [ ] Link memories to assistant
- [ ] Show filtered memories per assistant
- [ ] Reflection summary panel (optional stretch)

---

## ✅ Memory System

- [x] Memory saves from chat sessions
- [x] Transcripts + tags + embeddings are stored
- [x] Tags inferred via OpenAI + saved to DB
- [x] Memory list view in frontend

- [ ] Link `MemoryEntry.assistant` on save
- [ ] Enable filtering by assistant on memory view
- [ ] Add topic filter or tag search
- [ ] Show memory relevance or importance sorting

---

## ✅ Projects

- [x] Create new projects
- [x] View project detail page

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
