# 🧠 Phase Ω.8.1.c.2 — 🔍 Override Result Trace & Suppression Guard

## 🧭 Objective

Ensure that **anchor-matched chunks** intended for forced inclusion are:
- Explicitly visible in the serialized results
- Logged with justification
- Never silently suppressed or omitted from `/debug/rag-recall/`

This phase provides a traceable audit mechanism when anchor-injected chunks fail to appear in final assistant responses.

---

## 🔍 Problem Recap

Even after:
- Anchor-matched chunks were detected ✅
- `override_map` was populated ✅
- Glossary anchor was known ✅

...retrieved chunks still did not appear, and debug output shows:
- `Used Chunks: []`
- `forced_included: false`
- `override_reason: null`

This indicates that chunks were **not serialized**, **not displayed**, or **were filtered before scoring**.

---

## 🛠 Goals

### 🔹 1. Guaranteed Trace Path
- Log every chunk in `anchor_pairs`, whether used or not
- Show `forced_included: true/false` and `override_reason` in results
- Show `excluded_reason` if chunk was filtered or overwritten after injection

### 🔹 2. Result Debug Logging
Add per-chunk debug logs such as:
```python
logger.debug(f"[RAG Result] Chunk {chunk.id} | Score: {score:.4f} | Forced: {forced} | Reason: {reason}")
```

### 🔹 3. Suppression Guard
If any `anchor_pairs` chunk is **missing from result set**:
- Emit warning:
```python
logger.warning(f"[RAG ERROR] Anchor-linked chunk {chunk.id} missing from results — expected forced inclusion.")
```

---

## 🔧 Dev Tasks

### Backend
- [ ] Patch `chunk_retriever.py` to ensure:
  - All anchor-matched chunks are logged
  - `override_map` entries are visible in result serialization
  - Exclusion of any anchor chunk raises log warning

### Frontend
- [ ] In `/debug/rag-recall/`:
  - Mark all `anchor_matched_chunks`, even if unused
  - Add suppressed chunk badge: “Dropped after override” or “Filtered pre-score”

---

## 🧪 Verification Tests

| Case | Expected |
|------|----------|
| Anchor match, chunk used | `forced_included: true` in debug |
| Anchor match, chunk dropped | `forced_included: false`, `excluded_reason: low_score` |
| No match | No override metadata shown |

---

## 🔁 Related Phases
- Ω.8.1.c — Chunk Tracing
- Ω.8.1.c.1 — Debug Fix + Audit Replay
- Ω.7.21.d — Anchor Elevation Logic

---

## 🧠 TL;DR:
> An anchor-matched chunk must never disappear silently.  
> If it was retrieved, we log it. If it was dropped, we explain it.  
> This is myth-aligned retrieval you can trust.