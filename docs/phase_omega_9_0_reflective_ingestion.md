# Phase Ω.9.0 — Reflective Ingestion + Agent-Aware Memory

Phase Ω.9.0 finalizes the reflective ingestion pipeline. Documents uploaded through the API are chunked, embedded, reviewed by assistants, and transformed into reusable memories.

## End-to-End Checklist

- **Document Upload** – `/api/intel/ingest/` requires `assistant_id` and creates `Document` and `DocumentProgress` records.
- **Chunking & Embedding** – chunks store embeddings with a positive score and progress counts are tracked.
- **Assistant Review & Reflection** – `/assistants/:slug/review-ingest/:doc_id/` shows summaries and can trigger a reflection that stores a `MemoryEntry` and `AssistantReflectionLog`.
- **Chunk Debug & Repair** – the debug panel allows re-embedding, score fixes, and progress repair via `fix_doc_progress`.
- **Optional Agent Proposal** – reflections may generate an `AgentProposal` linking new tasks to the document.
- **Backend CLI Validation** – commands like `debug_check_document_embeddings` and `reembed_document` verify or reset embeddings.
- **Chat Retrieval Check** – assistants can answer document-based questions with context scores shown in debug metadata.

---
Prepares ingestion flows for agent-aware memory growth and swarm proposals.
