# 🧠 Phase Ω.8.1.d — Diagnostic Replay Patch

## 🧭 Objective

Create a mechanism to **capture failing RAG queries**, **snapshot their retrieval state**, and **enable deterministic replay** for audit and debugging. This phase builds a feedback loop for RAG truth integrity — especially when source chunks are skipped despite matching glossary terms and assistant alignment.

---

## 🔥 Problem Recap

Even with:
- Anchor matches ✅
- Glossary present ✅
- Assistant relevance ✅

...the system sometimes reports:
- ❌ No source used
- ❌ No chunks retrieved
- ❌ No debug trace emitted

This phase ensures every such case is logged, traceable, and reproducible.

---

## 🛠 Goals

### 🔹 1. RAG Failure Snapshot
- For each assistant query where:
  - `glossary_present == true` AND `used_chunks == []`
- Save:
  - Assistant slug
  - Query string
  - Glossary anchor(s)
  - Retrieved chunk pool
  - Raw/adjusted scores
  - Reflection content
  - Final assistant message

Store as `RAGFailureReplayLog`

---

### 🔹 2. Diagnostic Replay View
- New route: `/debug/rag-replay/:id`
- Loads failed query + all chunk metadata
- Shows:
  - What should’ve been used
  - What was skipped
  - Why it failed

### 🔹 3. Codex Replay Fixture Generation
- Auto-export log to JSON for Codex with:
```json
{
  "query": "what is the evm",
  "expected_chunks": ["chunk_32", "chunk_34"],
  "assistant_reflection": "EVM consistency and execution logic",
  "anchor_weight_profile": {"evm": 0.9},
  "retrieval_fallback": true
}
```

---

## 🔧 Dev Tasks

### Backend
- [ ] Create `RAGFailureReplayLog` model
- [ ] Save replay snapshot when forced chunks were skipped
- [ ] API: `GET /api/debug/rag-failures/` and `GET /api/debug/rag-replay/:id/`

### Frontend
- [ ] Build `RAGReplayViewer.jsx` for `/debug/rag-replay/:id`
- [ ] Add to sidebar under “Debug Tools”

---

## 🧪 Verification

- [ ] Query "What is the EVM?"
- [ ] Confirm failure snapshot logged
- [ ] Visit `/debug/rag-replay/:id` to review trace
- [ ] Confirm chunks with `evm` anchor shown but skipped
- [ ] Replay fixture generated for Codex if needed

---

## 🔁 Related Phases
- Ω.8.1.b — Anchor Weighting Logic
- Ω.8.1.c — Chunk Tracing
- Ω.8.1.c.2 — Suppression Guard

---

## 🧠 TL;DR:
> If RAG fails silently, the myth suffers. This patch captures the silence and gives you tools to speak its truth — one replay at a time.