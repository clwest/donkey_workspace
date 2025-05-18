# Embedding IO Helper

This document outlines how embeddings are generated, stored, and retrieved in the `intel_core` app.

## Overview

- Batches text chunks for OpenAI embedding API calls.
- Implements retry logic for rate limits and transient errors.
- Persists embeddings in `EmbeddingMetadata` and links back to `DocumentChunk`.

## Key Functions

- `generate_embeddings(chunks, model, batch_size)`
- `save_embedding(metadata)`
- `load_embedding(embedding_id)`

## Usage Examples

```python
from intel_core.helpers.embedding_io import generate_embeddings
embeddings = generate_embeddings(chunks, model="text-embedding-ada-002", batch_size=50)
```