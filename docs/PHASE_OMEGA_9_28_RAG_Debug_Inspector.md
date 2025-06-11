# Phase Ω.9.28 — RAG Debug Inspector + Glossary Insight Feedback

This phase ensures all RAG debug data, glossary misses, fallback reasoning, and recovery-triggered insights are fully inspectable, actionable, and traceable.

---

## ✅ Goals

- Finalize RAGGroundingLog visibility, boosting, and feedback flow
- Ensure glossary fallback causes (e.g. `"ignored"`, `"score_too_low"`) are traceable
- Display glossary misses and let users suggest glossary anchors
- Show which glossary anchors were automatically boosted and when
- Enable recovery reflections to auto-tag insights and glossary misses
- Confirm chat-grounding fallback logic is debuggable in full

---

## 🧠 Backend Tasks

- [x] Add `fallback_reason` field to `RAGGroundingLog` model (enum: ignored_glossary, no_chunks, no_match) — Completed 2025-06-04
- [x] Store fallback_reason on every `chat()` call when debug=true — Completed 2025-06-04
- [x] Link fallback_reason to glossary_hits and glossary_misses — Completed 2025-06-04
- [x] Tag new memories with `glossary_insight` when recovered from fallback — Completed 2025-06-04
- [x] Log missed glossary terms during chat and store in RAGGroundingLog — Completed 2025-06-04
- [x] Add `/assistants/<slug>/suggest_glossary_anchor/` [POST] for anchor suggestions — Completed 2025-06-04
- [x] Expose glossary_suggestion API with logging — Completed 2025-06-04

---

## 🧪 CLI Tools

- [x] `inspect_glossary_fallbacks` — audit fallback reasons from RAGGroundingLog — Completed 2025-06-04
- [x] `list_anchor_suggestions` — show all glossary suggestions — Completed 2025-06-04
- [x] `sync_fallback_tags` — re-tag memories with fallback_reason from grounding logs — Completed 2025-06-04

---

## 🖥️ Frontend Tasks

- [x] Add fallback_reason display to Chat Debug view — Completed 2025-06-04
- [x] Update RAG Debug Tab in AssistantDetailPage to show `fallback_reason` — Completed 2025-06-04
- [x] Allow clicking glossary_misses to open anchor suggestion modal — Completed 2025-06-04
- [x] Display glossary anchors marked as “boosted due to fallback” with a 🔁 icon — Completed 2025-06-04
- [x] Show suggested glossary anchors under the ChatDebug or RAGInspector component — Completed 2025-06-04
- [x] On `Repair Documents` or `Recovery`, append glossary_insight and show in memory timeline — Completed 2025-06-04

---

## 🧪 Tests + Verification

- [x] Test chat fallback logs appear in `/rag_debug/` — Completed 2025-06-04
- [x] Test glossary suggestions are saved — Completed 2025-06-04
- [x] Confirm chat with missing anchor triggers correct fallback_reason — Completed 2025-06-04
- [x] Confirm suggested anchors are marked in debug panel — Completed 2025-06-04
- [x] Validate document-linked reflections now add glossary tags if fallback_reason exists — Completed 2025-06-04

---

## 🧩 Phase Linkage

Follows: Ω.9.27 — Glossary Booster + Chunk Logging  
Leads into: Ω.9.29 — Memory Merge + RAG Replay Sandbox  
