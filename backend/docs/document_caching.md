# Document Caching Helper

This document covers Redis-based caching strategies used to speed up repeated ingestion or retrieval operations.

## Overview

- Caches raw and processed document content per session or request.
- Stores chunk lists and embedding lookups under structured Redis keys.
- TTL defaults and invalidation strategies to ensure freshness.

## Key Concepts

- Session cache vs. global cache
- Key namespace conventions: `intel_core:session:{session_id}:chunks`
- Default TTL: TODO

## Usage Examples

```python
from intel_core.helpers.document_caching import cache_chunks, get_cached_chunks
cache_chunks(session_id, chunks)
chunks = get_cached_chunks(session_id)
```  