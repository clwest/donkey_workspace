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

- [x] Add `fallback_reason` field to `RAGGroundingLog` model (enum: ignored_glossary, no_chunks, no_match)
- [x] Store fallback_reason on every `chat()` call when debug=true
- [x] Link fallback_reason to glossary_hits and glossary_misses
- [x] Tag new memories with `glossary_insight` when recovered from fallback
- [x] Log missed glossary terms during chat and store in RAGGroundingLog
- [x] Add `/assistants/<slug>/suggest_glossary_anchor/` [POST] for anchor suggestions
- [x] Expose glossary_suggestion API with logging

---

## 🧪 CLI Tools

- [x] `inspect_glossary_fallbacks` — audit fallback reasons from RAGGroundingLog
- [x] `list_anchor_suggestions` — show all glossary suggestions
- [x] `sync_fallback_tags` — re-tag memories with fallback_reason from grounding logs

---

## 🖥️ Frontend Tasks

- [x] Add fallback_reason display to Chat Debug view
- [x] Update RAG Debug Tab in AssistantDetailPage to show `fallback_reason`
- [x] Allow clicking glossary_misses to open anchor suggestion modal
- [x] Display glossary anchors marked as “boosted due to fallback” with a 🔁 icon
- [x] Show suggested glossary anchors under the ChatDebug or RAGInspector component
- [x] On `Repair Documents` or `Recovery`, append glossary_insight and show in memory timeline

---

## 🧪 Tests + Verification

- [x] Test chat fallback logs appear in `/rag_debug/`
- [x] Test glossary suggestions are saved
- [x] Confirm chat with missing anchor triggers correct fallback_reason
- [x] Confirm suggested anchors are marked in debug panel
- [x] Validate document-linked reflections now add glossary tags if fallback_reason exists

---

## 🧩 Phase Linkage

Follows: Ω.9.27 — Glossary Booster + Chunk Logging  
Leads into: Ω.9.29 — Memory Merge + RAG Replay Sandbox  
