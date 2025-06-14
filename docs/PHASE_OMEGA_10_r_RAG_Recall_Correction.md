# 🧠 Phase Ω.10.r — RAG Recall Correction + Memory Expansion

This phase improves glossary anchor precision and memory coverage.

## Goals
- Analyze weak anchor hits from `RAGGroundingLog` and rebuild missing links.
- Auto-suppress anchors with extremely poor scores or no linked chunks.
- Expand glossary candidates from frequently used memory tokens.
- Run `validate_anchors`, `inspect_rag_failure`, and `run_rag_tests` for affected assistants.

## Implementation Notes
- A new management command `rag_recall_correction` scans assistants with more than 100 anchors and under 10% match rate.
- The command re-links anchors using `generate_tags_for_memory`, adds new candidate anchors from memory entries, and runs diagnostic commands.
- Anchor diagnostics now expose `match_rate` and `auto_suppressed` fields.
