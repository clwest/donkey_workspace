# 🧠 Phase Ω.8.2 — Evolving Assistants Through Document Assignment

## 🧭 Objective

Replace the current "assistant-per-ingestion" flow with a new system that **assigns incoming documents to existing assistants**, enabling belief evolution, anchor enrichment, and coherent memory expansion over time.

---

## 🔄 Rationale

The current architecture creates a new assistant for every document set, leading to:
- Fragmented memory chains
- Duplicate glossary/anchor scoring
- Loss of identity, dream, and directive continuity

This phase establishes an **assistant-centered ingestion model**, letting existing agents *grow* their symbolic intelligence through new knowledge.

---

## 🛠 Goals

### 🔹 1. Assistant Assignment Flow
- On doc ingestion, allow user to:
  - Select an existing assistant (via dropdown or pre-selection)
  - Assign uploaded PDFs, YouTube links, or URLs directly to that assistant
- Store link in `Assistant.assigned_documents` or `AssistantMemoryChain`

### 🔹 2. Memory Enrichment
- Each assigned document:
  - Adds its summary to the assistant’s memory
  - Triggers glossary extraction and anchor weight profile update
  - Optionally generates a reflective `SwarmMemoryEntry` from the assistant’s POV

### 🔹 3. Dream-Preserving Ingestion
- Preserve assistant’s:
  - `dream_symbol`
  - `archetype`
  - `directive_nodes`
- Recalculate `preferred_rag_vector` if enough new content is added

### 🔹 4. Optional Reset: Codex-Assisted Fresh Start
- [ ] Wipe database of current assistants and embeddings
- [ ] Seed 3–5 clean assistants with curated roles
- [ ] Re-ingest Solidity, zk, and EVM docs into assigned assistants

---

## 🔧 Dev Tasks

### Backend
- [ ] Add document assignment relationship to `Assistant`
- [ ] Update ingestion pipeline to link doc → assistant
- [ ] Trigger memory + anchor enrichment on assignment

### Frontend
- [ ] Add assistant selector to doc upload modal
- [ ] Show per-assistant document list
- [ ] Add “Reflect on assigned docs” button per assistant

---

## 🧪 Verification

- [ ] Upload Solidity docs → assign to `solidity-dev-assistant`
- [ ] Confirm assistant memory includes doc summary
- [ ] Confirm anchor weights updated (e.g. `evm: +0.2`)
- [ ] Ask RAG question — check retrieval uses newly assigned docs

---

## 🔁 Related Phases
- Ω.8.1 — Dream Console, Anchor Scoring
- Ω.8.1.d — RAG Diagnostic Logging
- Ω.8.2.b (future) — Assistant Reflection on Assigned Knowledge

---

## 🧠 TL;DR:
> Let the assistant learn — not fork. Preserve the dream. Assign the document. Let them grow.