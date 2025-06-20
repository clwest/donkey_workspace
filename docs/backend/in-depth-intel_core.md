# intel_core App – In-Depth Module Reference

This document provides a comprehensive overview of the `intel_core` Django app, describing each file’s purpose, key classes/functions, and APIs available for reuse elsewhere in the project.

---

## 1. Top-Level Files

### 1.1 `apps.py`
- Purpose: Registers the app with Django.
- Key class: `IntelCoreConfig` (sets `default_auto_field` and `name`).
- Reusable API: None.

### 1.2 `admin.py`
- Purpose: Defines admin interfaces for core models.
- Models registered:
  - `DocumentAdmin`: displays title, source, created_at; searchable by title/content/url; filters by source/created_at.
  - `DocumentInteractionAdmin`: displays document, user, interaction_type, timestamp; searchable by document title/user; filters by type/timestamp.
  - `JobStatusAdmin`: displays job_id, status, progress; read-only created/updated; filters by status/created_at; disables manual add.

### 1.3 `models.py`
- Purpose: Defines core data models.
- Constants:
  - `EMBEDDING_MODEL`, `EMBEDDING_LENGTH`.
- Models:
  1. `Document`: UUID PK, title/slug generation, content, metadata, session_id, summary, status, M2M tags, timestamps.
     - `save()`: auto-slugifies title.
  2. `DocumentInteraction`: FK to Document & User, interaction_type, timestamp, metadata.
  3. `DocumentChunk`: FK to Document, order, text, tokens, chunk_type, fingerprint, OneToOne→`EmbeddingMetadata`.
  4. `DocumentFavorite`: unique user-document like table.
  5. `ChunkTag`: FK to DocumentChunk, name.
  6. `EmbeddingMetadata`: UUID PK, model_used, num_tokens, vector, status.
  7. `JobStatus`: UUID PK, status/progress/message/result JSON, timestamps.

### 1.4 `serializers.py`
- Purpose: REST Framework serializers for API responses.
- `DocumentSerializer`:
  - Fields: id, title, content, description, source_url, source_type, created_at, metadata, is_favorited.
  - `get_is_favorited()`: checks `DocumentFavorite` for current user.

### 1.5 `signals.py`
- *Deprecated*: previous versions used signals to maintain a `search_vector`
  field on `Document` models. That field has been removed, so the module now
  only contains a no-op stub for backward compatibility.

### 1.6 `tasks.py`
- Purpose: Celery background tasks for ingestion pipelines.
- Tasks (all update a `JobStatus` record):
  - `process_url_upload(...)`
  - `process_video_upload(...)`
  - `process_pdf_upload(...)`
  - Each: loads URLs/PDFs/videos via `intel_core.utils.ingestion`, updates progress, marks completed/failed, returns document count.

### 1.7 `urls.py`
- Purpose: Routes REST endpoints to view functions.
- Endpoints:
  - `POST /ingestions/` → `unified_ingestion_view`
  - `GET /documents/` → `list_documents`
  - `GET /documents/<uuid>/` → `document_detail_view`
  - `GET /documents/grouped/` → `list_grouped_documents`
  - `POST /documents/<uuid>/favorite/` → `toggle_favorite`
  - `POST /intelligence/summarize/<uuid>/` → `summarize_with_context`
  - `POST /intelligence/bootstrap-agent/<uuid>/` → `bootstrap_agent_from_docs`
  - `POST /intelligence/bootstrap-assistant/<uuid>/` → `create_bootstrapped_assistant_from_document`

---

## 2. View Packages (`intel_core/views/`)

### 2.1 `ingestion.py`
- `unified_ingestion_view(request)`:
  - Accepts `source_type` ∈ {`youtube`,`url`,`pdf`}, `urls`/files, optional title, project, session.
  - Delegates to `load_videos`, `load_urls`, or `load_pdfs` in `processors/`.
  - Returns serialized `Document` objects.

### 2.2 `documents.py`
- `list_documents(request)`: returns the latest version per (title,source_type) group.
- `document_detail_view(request, pk)`: full document detail, chunks, smart_chunks, summary, token count.
- `toggle_favorite(request, pk)`: toggles `DocumentFavorite` for user or fallback.
- `list_grouped_documents(request)`: groups by title/source_type/source_url, annotates total_tokens & count, returns entries per group.

### 2.3 `intelligence.py`
- `summarize_with_context(request, pk)`: GPT summary of first 3k chars.
- `bootstrap_agent_from_docs(request, pk)`: GPT → extracts JSON config (system_prompt, tone, personality, specialties).
- `create_bootstrapped_assistant_from_document(request, pk)`: GPT → parsed JSON → persists `Prompt`, `Assistant`, `AssistantProject`, `AssistantObjective`, `MemoryEntry`, `NarrativeThread`, linking the `Document`.

---

## 3. Core NLP Modules (`intel_core/core/`)

### 3.1 `constants.py`
- Loads spaCy, NLTK corpora; defines sentiment thresholds, ignore lists, patterns for name/topic extraction, embedding/chat model names.

### 3.2 `extractors.py`
- HTML title/keyword extraction, LSA summary (`sumy`), metadata generation, name extraction & validation, topic specificity checks.

### 3.3 `filters.py`
- Defines `ALL_STOP_WORDS` = sklearn’s English stopwords ∪ custom.

### 3.4 `text_processing.py`
- `clean_text(text)`, `lemmatize_text(text,nlp)` (with spaCy).

### 3.5 `topic_modeling.py`
- `get_topics(tfidf_matrix, feature_names, model_type)`: NMF/LDA topic extraction.
- `detect_topic(user_message)`: matches against `Topic` model keywords.

### 3.6 `transformers.py`
- TF-IDF & KeyBERT transforms, TextBlob sentiment, spaCy NER, topic models.

---

## 4. Helper Libraries (`intel_core/helpers/`)

### 4.1 Caching
- `cache_core.py`: wrappers around `django.core.cache`.
- `cache_helpers.py`: high-level model/session/user memory caching, decorators `@cached`, `memoize`.
- `cache_limits.py`: request-rate limiting helpers.
- `cache_models.py`, `cache_sessions.py`: simplified in-memory caches.

### 4.2 Document Helpers
- `document_helpers.py`: Playwright fetch (`fetch_url`, `fetch_webpage_metadata`), `extract_visible_text`, unified `get_documents`, `is_document_query`, `process_document_query`.
- `document_retrieval_helpers.py`: DB retrieval (`get_documents_by_type_and_title`, `get_document_by_id`), content cleaning/preview, content-quality filtering, `enhanced_document_context` for RAG.

### 4.3 Video Helpers
- `video_helpers.py`: high-level video document queries: `get_video_documents`, `get_video_titles`, `get_video_by_id`, `is_likely_video_query`.
- `youtube_video_helper.py`: YouTube ID extraction & transcript chunking via `youtube_transcript_api` & LangChain splitter.

### 4.4 NLTK Data Loader
- `nltk_data_loader.py`: thread-safe NLTK package downloads, avoiding redundant loads.

---

## 5. Utility Modules (`intel_core/utils/`)

### 5.1 `ingestion.py`
- High-level wrappers:
  - `ingest_pdfs(...)`, `ingest_urls(...)`, `ingest_videos(...)` → call respective `processors/*_loader.py`.

### 5.2 `processing.py`
- Core processing pipelines:
  - `generate_summary(text)` via OpenAI GPT; slug generation; `save_document_to_db(...)` (embedding, upsert `Document`, tagging, saving embedding).
  - `process_pdfs`, `process_urls`, `process_videos`: content cleaning, lemmatization, metadata enrichment → `save_document_to_db`.

### 5.3 `enhanced_chunking.py`
- `semantic_chunk_document(text, document_type, metadata)`: advanced chunking (section-aware, semantic boundaries, headings, TOC).

### 5.4 `cache_service.py`
- Unified cache interface: `InMemoryCache`, `RedisCache`, falls back to Django cache; supports get/set/delete/clear/get_many/set_many/incr, decorators.

---

## 6. Processors (`intel_core/processors/`)

### 6.1 `pdf_loader.py`
- `load_pdfs(file_paths, user_title, project, session)`: uses `PDFPlumberLoader` + text splitter → calls `process_pdfs` per chunk.

### 6.2 `url_loader.py`
- `load_urls(urls, user_title, project, session)`: fetches via Playwright, extracts visible text, splits → calls `process_urls` per chunk.

### 6.3 `video_loader.py`
- `load_videos(urls, user_title, project, session)`: fetches transcripts via `process_youtube_video`, loops chunks → calls `process_videos`.

---

## 7. Maintenance Scripts & Commands

### 7.1 `scripts/backfill_document_slugs.py`
- Standalone script to populate missing `Document.slug` values (ensures uniqueness).

### 7.2 `management/commands/backfill_embeddings.py`
- Django management command: for each `DocumentChunk` missing an `EmbeddingMetadata` record, generates an embedding for the chunk text and links it back to the chunk.

---

## 8. Testing
- `intel_core/tests/`: pytest modules covering cache behavior, chunking logic, document service functions, embedding I/O, enhanced chunker strategies.

---

This reference should serve as your roadmap to the `intel_core` app’s structure, data flows, and reusable components. Feel free to link functions, import classes, or adapt the patterns provided here in other parts of the project.