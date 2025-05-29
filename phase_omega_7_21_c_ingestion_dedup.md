# 🧠 Phase Ω.7.21.c — Ingestion Deduplication & Fallback Suppression

## 🩺 Problem
Solidity document ingestion is **executing twice**:
- First pass extracts full content and ~35 valid chunks
- Second pass re-runs on a degraded/plaintext version (~168 tokens), leading to duplicated or weakened chunk sets

This is likely caused by fallback reprocessing, missing deduplication logic, or redundant triggers from document loaders and async tasks.

---

## 🛠️ Goals

### 🧱 1. Chunk Existence Guard
- Before reprocessing a URL, check if valid `DocumentChunk` records already exist
- Skip ingestion and log a warning if chunks are already stored

### 🧠 2. Log Task Source
- Inside `create_document_set_task`, log:
  - The document set triggering it
  - The session_id or request source if available
  - The list of incoming URLs

### 🧪 3. Prevent Double-Parsing
- Ensure `load_url()` or `clean_text()` isn't being called again by fallback triggers like:
  - Model post-save signals
  - Redundant manual `document.save()` after parsing

---

## 🔧 Dev Tasks

### 🔹 Backend
- [ ] In `load_urls.py`, add:
```python
if DocumentChunk.objects.filter(document=document).exists():
    logger.warning(f"[Ingest] Skipping {url} — chunks already exist.")
    return document
```

- [ ] In `create_document_set_task`, add:
```python
logger.info(f"[Task Start] Triggered by DocumentSet {document_set.id} | URLs: {urls} | Session: {session_id}")
```

- [ ] Audit if fallback ingest calls `load_url()` or `clean_text()` twice and suppress second call

---

## 🧪 Test Verification

- [ ] Ingest same Solidity URL — only one pass logs
- [ ] `/debug/chunks/<doc_id>/` shows only ~35 expected chunks
- [ ] No degraded ~168-token duplicate versions appear
- [ ] Assistant retrieval behavior matches glossary-linked chunks

---

## 🔁 Linked Phases

- Ω.7.20.b — Solidity Ingestion Fix
- Ω.7.21 — Chunk Glossary Match Scoring
- Ω.7.21.b — Anchor Boost Tuning