
# ✅ Donkey Betz AI — Phase Ω.8.0: RAG Lock-In & Dynamic Knowledge Ingestion

## 🧭 Objective
Stabilize and polish the current Retrieval-Augmented Generation (RAG) system, then add support for dynamically expanding an agent's knowledge base via document uploads, links, or direct input.

---

## 🔍 Phase 1: RAG Lock-In (Stabilize & Trust the Brain)

### 🔹 Chunk Traceability & Fingerprinting
- [ ] Display fingerprints and token counts per chunk in debug panel
- [ ] Confirm unique fingerprints are reliably stored and retrievable
- [ ] Add chunk creation logs (if not already present)

### 🔹 Glossary Anchoring + Diagnostics
- [ ] Visualize missing anchors or glossary terms in the UI
- [ ] Add fallback behavior: "Suggest new glossary entry" when anchor miss occurs
- [ ] Create glossary patch queue (editable/fillable missing terms)

### 🔹 Source Confidence & Reasoning Transparency
- [ ] Add source match confidence bar (e.g., 0.86 match score)
- [ ] Implement “why this chunk?” tooltip showing anchor, chunk ID, and score
- [ ] Include assistant reflection logs to evaluate source coverage

### 🔹 Debug Panel Enhancements
- [ ] Color code good source / stale / ambiguous chunk matches
- [ ] Show SymbolicMemoryAnchor metadata and link to chunk set
- [ ] Enable “refresh” or “reinspect” button for anchor-chunk state

---

## 🧠 Phase 2: Agent Knowledge Expansion (Make It Learn)

### 🔹 Upload/Ingest Flow
- [ ] Add “Upload Knowledge” button to agent page
- [ ] Support input types: 
  - [ ] PDF
  - [ ] URL
  - [ ] Plain text
- [ ] Route: `POST /agents/:id/upload_knowledge/`
  - [ ] Calls chunking + embedding pipeline
  - [ ] Stores document with tag + agent reference
  - [ ] Auto-assigns new symbolic anchors

### 🔹 Metadata & Context Tracking
- [ ] Track who uploaded the doc + timestamp
- [ ] Add chunk tags for source (e.g. “foundry”, “viem”, etc.)
- [ ] Allow override: user defines glossary term on upload

### 🔹 Growth UI
- [ ] Show "Knowledge Growth Log" per agent
- [ ] Filter by tag, date, source, or anchor
- [ ] Allow re-processing of chunks if agent behavior changes

---

## 🔄 BONUS: Symbolic Reflection Engine v2
- [ ] Let agents reflect on their updated knowledge
- [ ] Log summary of new topics learned
- [ ] Suggest new anchors or glossary terms from ingested text

---

### 🧠 TL;DR:
> Lock the brain. Then feed it knowledge. Then let it evolve.
