# RAG-Flow

The ingestion pipeline now links uploaded documents directly to an existing assistant. `POST /api/intel/ingest/` **requires** `assistant_id` and stores each document and chunk under that assistant.

After ingestion the assistant can review the content via `/api/assistants/{slug}/review-ingest/{doc_id}/` which triggers `reflect_on_document()`. The reflection is saved as a `MemoryEntry` and can spawn follow‑up tasks or new agents.

Bootstrapping a new assistant from a document is available only through the sandbox route `/api/intel/experiments/bootstrap-from-doc/<uuid>/`.
