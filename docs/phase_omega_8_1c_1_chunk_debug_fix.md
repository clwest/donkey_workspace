# 🧠 Phase Ω.8.1.c.1 — RAG Chunk Trace Debug Fix & Audit Replay

## 🧭 Objective

Ensure that the implementation of Phase Ω.8.1.c actually surfaces **anchor-aligned chunk behavior** in debug views and **guarantees forced inclusion** during retrieval. The backend code exists, but the output suggests either logging suppression, forced inclusion not working in practice, or the frontend is missing key visibility.

---

## 🔍 Observed Issues

- ✅ Glossary tags and embeddings are working
- ✅ Assistant debug shows symbolic anchors like `zk-rollup`
- ❌ RAG fallback still triggers with `Used Chunks: []`
- ❌ No `forced_included`, `override_reason`, or adjusted scores appear in `/debug/rag-recall/`

This phase re-verifies the full path from anchor → retrieval → ranking → inclusion → debug trace.

---

## 🛠️ Goals

### 🔹 1. Expose Forced Inclusion in Debug Output
- `/debug/rag-recall/` must include:
  - `forced_included: true/false`
  - `override_reason: anchor-match`
  - `score_before_anchor_boost`, `score_after_anchor_boost`
- If any chunk was matched by anchor and not used, log:
  - `"Anchor-matched chunk [id] skipped — reason: [e.g., low raw score]"`

### 🔹 2. UI Fixes
- Debug sidebar should show:
  - Forced inclusion icon or badge
  - Reason for inclusion or exclusion
  - If a fallback was used, show which anchor was missed and what chunks were skipped

### 🔹 3. RAG Replay Tool (Optional)
- Add a `replay=true` query param to `/debug/rag-recall/` to reload a past retrieval with full trace overlays
- Useful for regression testing and anchor performance audits

---

## 🔧 Dev Tasks

### Backend
- [ ] Ensure `override_map` entries are fully logged
- [ ] Confirm fallback conditions log missed anchors + reasons
- [ ] Expose `retrieved_chunks`, `filtered_chunks`, and `anchor_matched_chunks` explicitly

### Frontend
- [ ] Show `forced_included`, `override_reason`, and score diffs in UI
- [ ] Highlight chunks in debug view if anchor-aligned but dropped
- [ ] Tooltip or badge: “Included due to anchor match” or “Excluded despite anchor match”

---

## 🧪 Verification

| Query | Anchor | Chunk Status |
|-------|--------|--------------|
| What is the EVM? | `evm` | Chunk ID shown in used list with `forced_included: true` |
| zk-rollup benefits | `zk-rollup` | Score adjusted, included with boost |
| Solidity contract structure | `smart-contract` | Anchor match traced and visible |

---

## 🔁 Related Phases
- Ω.8.1.b — Anchor Weighting
- Ω.8.1.c — Glossary Chunk Tracing
- Ω.7.21.d — Anchor Override Logic

---

## 🧠 TL;DR:
> Don’t just log it — trace it, tag it, and explain it.  
> This phase brings chunk reasoning into full visibility.