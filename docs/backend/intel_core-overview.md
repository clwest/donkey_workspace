# Intel Core App Overview

## Core Models
- **Document**: Primary ingested document with metadata, source info, summary and tags.
- **DocumentInteraction**: Tracks user interactions with a document.
- **DocumentChunk**: Stores text chunks with embedding metadata.
- **DocumentFavorite**: Many-to-many favorite relation for users.
- **ChunkTag**, **EmbeddingMetadata**, **JobStatus** for chunk tagging and processing state.

## Serializers
- `DocumentSerializer` used for listing and detail responses.

## Views & Endpoints
- `unified_ingestion_view` `/intel_core/ingestions/` – ingest YouTube, PDF or URL content.
- `list_documents` and `document_detail_view` for retrieval.
- `list_grouped_documents` groups latest docs.
- Intelligence endpoints under `/intel_core/intelligence/` for summarization and bootstrapping assistants from documents.

## Utilities
- `processors` package handles loading from URLs, PDFs, and videos.
- `helpers` modules provide embedding cleanup and token helpers.

## Dependencies
- Links to `prompts`, `assistants`, and `memory` when bootstrapping or summarizing.
- Uses OpenAI to generate content and embeddings.
