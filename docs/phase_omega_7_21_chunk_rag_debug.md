# 🧠 Phase Ω.7.21 — Chunk Glossary Match Scoring + RAG Recall Debug

## 🎯 Objective
Enhance assistant RAG performance **by surfacing per-chunk glossary match scores** and giving devs tools to verify if the assistant is recalling the *right chunks* based on glossary anchors.

---

## 🛠️ Summary of Goals

### 🔍 1. Add per-chunk glossary match scoring
- Score how well each chunk aligns with glossary anchors (e.g., `zk-rollup`, `evm`, `gas cost`)
- Store score as `glossary_score` in chunk debug metadata
- Include matched anchors as a list (`["evm", "zk-rollup"]`)

### 💬 2. Extend `/debug/chunks/<doc_id>/` to show:
- `glossary_score` per chunk (e.g., 0.92 for solid match)
- Matched anchor terms
- Token count per chunk
- Fingerprint, chunk ID, and content preview

### 🧠 3. Add `/debug/rag-recall/?query=...&assistant=...` endpoint
- Simulates RAG for a given query
- Logs top retrieved chunks, their glossary scores, and anchor alignment
- Ideal for queries like:
  - "How does the EVM execute instructions?"
  - "zk-rollup scaling advantages?"
  - "Smart contract storage structure?"

---

## 🚀 Dev Tasks

### 🔹 Backend
- [ ] Update chunk metadata model to include `glossary_score` and `matched_anchors`
- [ ] Add scoring logic during chunk embedding or glossary pass
- [ ] Extend `/debug/chunks/<doc_id>/` with full scoring info
- [ ] Create `/debug/rag-recall/` view to simulate a retrieval and return detailed matches

### 🔹 Frontend
- [ ] Display glossary scores + anchors per chunk on chunk detail page
- [ ] Add input box for testing RAG queries and showing scored results inline
- [ ] Highlight strong vs weak glossary matches visually (green/yellow/red)

---

## 🧪 Dev Verification
Use this checklist after implementation:
- [ ] Are all top-matching chunks aligned with glossary terms?
- [ ] Do glossary scores reflect term density / overlap?
- [ ] Is assistant behavior improved on anchor-heavy queries?

---

## 🔁 Linked Context
- Assistant: `solidity-dev-assistant`
- Glossary Anchors: `smart-contract`, `zk-rollup`, `ethereum-virtual-machine`
- Related Phase: Ω.7.20.b — Ingestion Fix & Chunk Debug Preview