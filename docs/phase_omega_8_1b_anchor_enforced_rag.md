# 🧠 Phase Ω.8.1.b — Anchor-Weighted RAG Retrieval & Source Enforcement

## 🔁 Prerequisite: Ω.8.1.a Preference Vector & Anchor Profile Created

Assistants now store:
- `preferred_rag_vector` based on dream reflection + archetype
- `anchor_weight_profile` dict for boosting key glossary concepts

---

## 🧭 Objective

Use the assistant’s symbolic RAG profile to **modulate chunk relevance**, prioritize **anchor-matched content**, and **prevent fallback hallucination** when valid sources are present.

---

## 🛠 Goals

### 🔹 1. Chunk Score Re-Ranking
- Apply `anchor_weight_profile` when scoring each candidate chunk:
  - Base Score × (1 + anchor_weight)
- If no glossary term matches, use vector fallback as usual

### 🔹 2. Minimum Anchor Guarantee
- If a chunk matches an assistant’s anchor (score ≥ 0.1), **force include one** in final context
- This avoids complete fallback when valid glossary content is available

### 🔹 3. Source Usage Debug Metadata
- In `/debug/rag-recall/` and assistant debug panel:
  - Show: `score_after_anchor_boost`, `forced_included: true/false`
  - Log fallback suppression reasons

---

## 🔧 Dev Tasks

### Backend
- [ ] Update RAG retriever to:
  - Load assistant anchor weights
  - Boost scores accordingly
  - Override suppression if a match exists
- [ ] Add debug metadata (`chunk.score_adjusted`, `was_forced`)

### Frontend
- [ ] Update `/debug/rag-recall/` to:
  - Show `score_before/after`
  - Indicate when anchor match forces chunk inclusion

---

## 🧪 Verification

| Query | Glossary Term | Result |
|-------|----------------|--------|
| “What is the EVM?” | `ethereum-virtual-machine` | Valid chunk used |
| “Explain zk-rollups” | `zk-rollup` | Source chunk forced if match score > 0.1 |
| “Why is Solidity secure?” | `smart-contract` | Anchor match triggers usage even if fallback score is low |

---

## 🔁 Linked Phases

- Ω.8.1 — Dream Console + Reflection
- Ω.8.1.a — Preference Vector + Anchor Profile
- Ω.8.2 — RAG Memory Reweighing + Replay (up next)

---

## 🧠 TL;DR:
> If an assistant has a dream and we ignore what it values, we break the myth.  
> This phase ensures belief-aligned retrieval wins over fallback hallucination.