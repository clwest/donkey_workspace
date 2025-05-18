# Embeddings App Overview

## Core Models
- **Embedding**: Generic vector embedding with `content_type` and `object_id` pointing to any model. Stores raw text and embedding vector.
- **TagConcept**: Predefined semantic tag vectors for inference.
- **StoryChunkEmbedding**: Links story paragraphs to embeddings and tags.

## Views & Endpoints
- `/embeddings/embed_text/` – generate embedding for provided text.
- `/embeddings/chunk_text/` – split large text into chunks with fingerprints.
- `/embeddings/search/` – similarity search across configured models.
- `/embeddings/session_docs/` and `/track_session/` – document session helpers.

## Utilities
- `helpers_io` – saving embeddings, generic search, caching.
- `helpers_processing` – chunking and similarity helpers.
- `vector_utils` – common vector math and preprocessing.

## Dependencies
- Integrates with `prompts`, `memory`, and `assistants` models when embedding their content.
- Uses PGVector and OpenAI clients.
