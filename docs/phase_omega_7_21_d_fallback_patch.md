# 🧠 Phase Ω.7.21.d — Glossary-Fallback Elevation & Junk Chunk Suppression

## 🧩 Problem
Despite correct glossary tag matches (`zk-rollup`, `evm`, `smart-contract`), RAG fallback still delivers **low-score junk chunks** (e.g., score = 0.1881). This leads to assistant replies like:

> “I couldn’t find that information in the provided memory.”

Even worse, the assistant forks due to **anchor miss**, when the correct content **was present** but hidden beneath weak vector similarity rankings.

---

## 🎯 Objective
Improve RAG recall behavior when glossary matches are found by:

1. **Forcing elevation of glossary-linked chunks**, even if similarity score is low
2. **Suppressing fallback junk chunks** with scores under a cutoff (e.g. < 0.2)
3. **Logging fallback reasons** and override justification

---

## 🛠️ Dev Tasks

### 🔹 Backend

#### ✅ 1. Elevate glossary-linked chunks
- If a query matches an anchor (e.g., `zk-rollup`), inject at least 1 matching chunk **regardless of vector score**

#### 🚫 2. Suppress weak fallback junk
- Discard chunks with `score < 0.2` unless:
  - It’s part of an anchor override
  - It contains glossary-linked content

#### 🔍 3. Log override reasons in debug
- In `/debug/rag-recall/`, add:
  - `override_reason`: `anchor-match` or `low-score-junk`
  - `suppressed`: `true/false` for fallback candidates

### 🔹 Frontend

- [ ] In RAG recall debug view:
  - Highlight anchor-matched overrides with a badge
  - Show suppressed fallback chunks if debug mode is enabled

---

## 🧪 Verification Checklist

| Condition | Expectation |
|----------|-------------|
| Query: “Explain a ZK-Rollup” | Chunk with `zk-rollup` anchor included, even if score = 0.15 |
| Query: “What is the EVM?” | `evm` chunk appears in recall, no junk fallback |
| Low-score chunk (score < 0.2) without glossary anchor | ✅ Suppressed |

---

## 🔁 Related Phases
- Ω.7.21 — Glossary Match Scoring
- Ω.7.21.b — Anchor Boost Tuning
- Ω.7.21.c — Ingestion Deduplication

---

## 🧠 Status Triggered From
- Assistant: `solidity-dev-assistant`
- Trigger: `anchor_miss:zk-rollup`
- Observed: junk fallback chunk, score 0.1881