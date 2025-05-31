# 🧠 Phase Ω.8.1.e — RAG Failure Table Viewer UI

## 🧭 Objective

Surface all logged RAG retrieval failures in a **debuggable frontend table**, enabling devs to:
- Review failed queries
- See expected anchors vs. used chunks
- Identify when/why source alignment failed

This ties the failure logging loop into a live Codex-aware debug panel and prepares for future reprocessing, score tuning, and assistant reflection on missed content.

---

## 🛠️ Goals

### 🔹 1. RAG Failure Log Table
- New route: `/debug/rag-failures`
- Displays all entries logged by `update_rag_failure_log.py`

Columns:
| Query | Assistant | Anchor(s) | Used Chunks | Expected Chunks | Reason |
|-------|-----------|-----------|-------------|-----------------|--------|

### 🔹 2. Row Drilldown
- Clicking a row navigates to `/debug/rag-replay/:id`
- Replay shows chunk scores, override flags, and assistant context

### 🔹 3. Badge Rendering
- Badge for each anchor in row
- Color-coded `Reason`: red for `missing source`, yellow for `filtered out`, etc.

---

## 🔧 Dev Tasks

### Frontend
- [ ] Create `RAGFailureTable.jsx`
- [ ] Add route `/debug/rag-failures` to router
- [ ] Load JSON from `/static/rag_failures.json` or backend API
- [ ] Enable per-row drilldown to `/debug/rag-replay/:id`

### Backend (Optional)
- [ ] Expose `/api/debug/rag-failures/` if you want dynamic serving
- [ ] Parse existing log file into paginated endpoint

---

## 🧪 Verification

- [ ] Submit broken queries (e.g. “What is the EVM?”)
- [ ] Confirm failures are logged to file
- [ ] View at `/debug/rag-failures`
- [ ] Click row → see `/debug/rag-replay/:id`
- [ ] Confirm chunk score and anchor trace present

---

## 🔁 Related Phases
- Ω.8.1.d — Failure Logging
- Ω.8.1.c — Chunk Override Guard
- Ω.8.2 — Self-Healing RAG Agents (next)

---

## 🧠 TL;DR:
> We caught the failure. Now we give it a name, a row, a button — and a plan to evolve from it.