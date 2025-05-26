# Document Caching Helper

This document covers Redis-based caching strategies used to speed up repeated ingestion or retrieval operations.

## Overview

- Caches raw and processed document content per session or request.
- Stores chunk lists and embedding lookups under structured Redis keys.
- TTL defaults and invalidation strategies to ensure freshness.

## Key Concepts

- Session cache vs. global cache
- Key namespace conventions: `intel_core:session:{session_id}:chunks`
- Default TTL: **24 hours** for both document embeddings and session keys.
- Invalidation: cached entries expire automatically via TTL and can be cleared
  on demand using `clear_session_data` or `delete_cache` from
  `intel_core.helpers.cache_helpers`.

## Usage Examples

```python
from intel_core.helpers.cache_helpers import (
    store_session_data,
    get_session_data,
    clear_session_data,
)

# Cache chunk list for a session (expires after 24 hours by default)
store_session_data(session_id, "chunks", chunks, ttl=60 * 60 * 24)

# Retrieve cached chunks later
chunks = get_session_data(session_id, "chunks")

# Invalidate manually when processing completes
clear_session_data(session_id, "chunks")
```
