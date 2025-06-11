# 📦 Codex Sprint Tasks (as of Ω.9.90)

This file is a living task list for Codex-generated backend + frontend development.

---

## ✅ Completed

- [x] Ingestion error tracking (Document.progress_error)
- [x] Prevent reflection without embedded memory
- [x] Add fallback summary chunk injection
- [x] Fix `embed_and_store` NameError bug
- [x] Deduplicate fallback chunk fingerprints

---

## 🛠 Active Backend Tasks

- [ ] Auto-link ingested documents to assistant.memory_context
- [ ] Save `user_id` on Document during ingestion
- [ ] Persist `generated_prompt_id` after reflection prompt creation
- [ ] Add CLI: `validate_embedded_chunks --repair`

---

## 🎯 Active Frontend Tasks

- [ ] Fix `DocumentIngestingCard` polling and render bug
- [ ] Display `progress_error` reason in UI
- [ ] Show link to reflection prompt on completed cards
- [ ] Add toggle to show symbolic insight logs in `/assistants/:slug/`

---

## 🧠 Suggested Refactors

- [ ] Consolidate vector storage (use only Embedding.vector on DocumentChunk)
- [ ] Create `RAGPlaybackPanel` to inspect memory usage per chat
- [ ] Refactor assistant detail page to show glossary, memory, insights in tabs

---

## 🧬 Meta

- [ ] All new Codex prompts must reference `ROADMAP.md` and `PHASE_SUMMARY.md`
- [ ] Glossary drift tracking logs must link to assistant.slug
