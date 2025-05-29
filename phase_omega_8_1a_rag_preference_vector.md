# 🧠 Phase Ω.8.1.a — Dream-Based RAG Preference Vector & Anchor Weighting

## ✅ Prerequisite: Phase Ω.8.1 Completed

The assistant onboarding system now supports:
- Archetype + dream symbol selection
- Dream initiation via `/dream/initiate/`
- Creation of symbolic memory + directive node from reflection

---

## 🧭 Objective

Use the onboarding dream reflection, archetype, and selected symbols to generate a **personalized RAG preference vector** and **anchor weighting profile** for each assistant.

This improves RAG relevance by:
- Biasing chunk scoring toward aligned anchors
- Providing symbolic weighting for retrieval decisions
- Enabling assistant-specific chunk prioritization in fallback scenarios

---

## 🧠 Goals

### 🔹 1. RAG Preference Vector
- A semantic embedding based on:
  - Archetype description
  - Dream symbol meaning
  - First reflection text
- Stored in assistant model as `preferred_rag_vector` (OpenAI or internal embedding)

### 🔹 2. Anchor Weight Profile
- Dictionary of glossary anchor → weight score:
```json
{
  "zk-rollup": 0.8,
  "evm": 0.7,
  "gas-optimization": 0.6
}
```
- Based on assistant type, reflection keywords, and user-selected anchors
- Used as a boosting factor in retrieval

### 🔹 3. RAG Enhancer Hook
- During chunk retrieval:
  - Use similarity to `preferred_rag_vector` to modulate scores
  - Apply anchor weights as additive/re-ranking multipliers

---

## 🔧 Dev Tasks

### Backend
- [ ] Add `preferred_rag_vector` and `anchor_weight_profile` to Assistant model
- [ ] Implement `generate_rag_profile_from_reflection(assistant)` helper
- [ ] Inject weighting logic into RAG retriever pipeline

### Frontend
- [ ] Add "View RAG Profile" button in Dream Console
- [ ] Display matched anchors, weights, and profile preview

---

## 🧪 Verification

- [ ] Assistant reflection results in embedded profile
- [ ] `/debug/rag-recall/` shows anchor-weighted results
- [ ] Assistants retrieve aligned chunks more effectively in weak-score queries

---

## 🔁 Linked Phases

- Ω.8.0 — RAG Trust & Upload
- Ω.8.1 — Dream Console
- Ω.8.2+ — Adaptive Retrieval + Symbolic Replay

---

## 🧠 TL;DR:
> When an assistant dreams, it doesn’t just awaken — it aligns.  
> Let that dream shape how it listens to the world.