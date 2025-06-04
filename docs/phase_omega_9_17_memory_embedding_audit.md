# Phase Ω.9.17 — Memory + Embedding Link Audit

This phase introduces management tools and model tweaks to verify that assistant memories and document embeddings remain properly linked.

## Key Updates
- **MemoryEntry** now auto-creates a `MemoryContext` if missing and aligns its `target_object_id`.
- **DocumentChunk** gains `embedding_valid` and `has_glossary_score` for auditing vector health.
- **AssistantReflectionLog** can link back to `PromptUsageLog` for full prompt traceability.
- New management commands:
  - `inspect_memory_links` – reports orphaned memories and missing transcripts.
  - `check_chunk_embedding_status` – detects missing or invalid embeddings and glossary-score issues.

Run the commands with an optional `--assistant` slug to focus on a single assistant.
