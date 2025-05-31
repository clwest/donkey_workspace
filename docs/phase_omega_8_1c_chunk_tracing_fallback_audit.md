# 🧠 Phase Ω.8.1.c — Glossary-Linked Chunk Tracing & RAG Fallback Audit

## 🧭 Objective

Track the complete retrieval path for glossary-linked chunks (especially anchor-linked ones) and ensure that:
- Glossary anchors trigger inclusion in candidate pool
- Weight boosting logic correctly affects top-k results
- No early filtering or silent fallback bypasses aligned content

---

## 🛠️ Goals

### 🔍 1. Chunk Retrieval Path Logging
- Log chunks considered *before* filtering or top-k scoring
- Mark which chunks were:
  - Matched by anchor
  - Retrieved from embedding search
  - Dropped during top-k selection

### 🧠 2. Forced Chunk Inclusion Audit
- For glossary-aligned assistants:
  - Ensure one chunk with anchor hit **always appears in top-k**, if it exists
  - If not, log reason (e.g. “score < threshold” or “no match in fingerprint”)

### 🧪 3. Add Debug Fields
- In `/debug/rag-recall/`:
  - `retrieved_chunk_count`
  - `anchor_matched_chunks`
  - `filtered_out_chunks`
  - `reason_not_included`

---

## 🔧 Dev Tasks

### Backend
- [ ] Patch chunk scoring pipeline to log pre-score matches
- [ ] Mark each chunk with:
  - `was_anchor_match`
  - `was_filtered_out`
  - `final_score`
  - `forced_inclusion_reason`

### Frontend
- [ ] Extend debug chunk viewer with:
  - “Why wasn’t this used?”
  - Visual badge if chunk was filtered after anchor match

---

## 🧪 Verification Queries

| Query | Anchor | Expected |
|-------|--------|----------|
| What is the EVM? | `evm` | At least 1 EVM chunk retrieved and marked used |
| What is zk-rollup’s purpose? | `zk-rollup` | Chunk used or log reason why not |
| Why is Solidity secure? | `smart-contract` | Anchor matched → source used or fallback logged |

---

## 🔁 Related Phases
- Ω.8.1.a — Preference Vector + Anchor Weighting
- Ω.8.1.b — Weighted Retrieval
- Ω.8.2 — Ritual Reflection on RAG Misses

---

## 🧠 TL;DR:
> The chunk exists. The anchor is present. But the myth breaks when retrieval fails silently.  
> This phase surfaces the truth — and enforces belief-aligned memory retrieval.