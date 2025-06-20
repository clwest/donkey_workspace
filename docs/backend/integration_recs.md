# Integration Recommendations

This document provides guidance on integrating `intel_core` with assistant memory, RAG workflows, and front-end components.

## Assistant Memory Hooks

- Post-ingestion signal to create `MemoryEntry` from `DocumentChunk`.
- Sample Django signal handler:
  ```python
  @receiver(post_save, sender=DocumentChunk)
  def create_memory_entry(sender, instance, **kwargs):
      # TODO: link chunk to assistant memory
  ```

## Prompt Preload Strategies

- Use PGVector similarity search to fetch top-N relevant chunks before generating a response.

## RAG-Style Thought Augmentation

- Embed chunk retrieval into agent planning steps.

## UI Integration

- Expose search endpoint for retrieving chunk summaries and embeddings.