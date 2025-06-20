# Performance Considerations

This document highlights key performance and scaling considerations for `intel_core`.

## Redis Usage

- Monitor cache hit/miss rates.
- Tune TTLs to balance freshness vs. recomputation.

## PGVector Operations

- Ensure proper vector index types (HNSW or ivfflat) for search.
- Consider async embedding writes to avoid request blocking.

## Embedding Rate Limits

- Batch calls to OpenAI API to respect rate limits.
- Implement exponential backoff on failures.