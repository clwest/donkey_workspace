# Models

This document provides an overview of the core data models in the `intel_core` app.

---

## Document

**Purpose:** Represents an ingested source document (URL, PDF, transcript, raw text).

**Key Fields:**

- `title`: Human-readable title
- `source_url`: Original URL (optional for PDFs or pasted text)
- `source_type`: Enum (url, pdf, youtube, etc.)
- `status`: Ingestion status (pending, complete, failed)
- `tags`: Optional document-level metadata
- `token_count`: Optional total tokens across chunks
- `source_language`: Optional ISO language code
- `ingested_by`: ForeignKey to User
- `created_at`, `updated_at`: Timestamps

**Indexes & Constraints:**

- ✅ Unique constraint: `source_url` (nullable)
- ✅ Index on `status`, `source_type`, `created_at`

**Relationships:**

- ➡️ One-to-many with `DocumentChunk`

---

## DocumentChunk

**Purpose:** Stores a segment of a document optimized for embeddings and RAG.

**Key Fields:**

- `document`: ForeignKey to `Document`
- `order`: Integer sequence within doc
- `text`: Chunk contents
- `tokens`: Token count
- `chunk_type`: Enum (intro, body, quote, summary, etc.)
- `fingerprint`: SHA256 hash for deduplication
- `is_summary`: Optional boolean for extracted summaries
- `embedding`: ForeignKey to `EmbeddingMetadata`

**Indexes & Constraints:**

- ✅ Unique: (`document`, `order`)
- ✅ Index on `fingerprint`

---

## ChunkTag

**Purpose:** Tags for filtering, searching, or classifying chunks.

**Fields:**

- `chunk`: FK to `DocumentChunk`
- `name`: Tag name (string or slug)
- `created_at`: Timestamp

**Future Notes:**

- 🔄 Could be unified with `mcp_core.Tag` model.

---

## EmbeddingMetadata

**Purpose:** Stores metadata + vector output from OpenAI or other embedding models.

**Fields:**

- `embedding_id`: UUID or external ref
- `vector`: PGVector field (normalized)
- `model_used`: E.g., "text-embedding-3-small"
- `num_tokens`: Input token count
- `status`: Enum (pending, complete, failed)
- `source`: FK to `DocumentChunk` (or generic foreign key in future)
- `created_at`, `updated_at`: Timestamps

**Indexes:**

- ✅ PGVector `vector` should have an ANN index
- ✅ Index on `model_used`, `status`

---

## TODO Summary

- [ ] Clean out old migrations
- [ ] Apply model field tweaks
- [ ] Generate fresh migration
