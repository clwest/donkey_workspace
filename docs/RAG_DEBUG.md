# RAG Debug Summary

This document tracks repair operations for RAG chunk retrieval.

- `repair_rag_chunk_links` fixes missing document context links and invalid embedding references.
- `embedding-debug` panel now shows retrieval counts per assistant when toggled.

Run `python manage.py repair_rag_chunk_links` after seeding to ensure all links are valid.

✅ Phase Ω.9.139 — RAG Link Repair + Embedding Debug Integrity

🧠 Goals Addressed

This phase repaired foundational inconsistencies in the RAG pipeline by ensuring all embeddings, documents, chunks, and assistant contexts are properly connected.

⸻

🔧 Backend Fixes

Embedding Link Repair
• ✅ Implemented fix_embedding_links() service to:
• Patch broken object_id, content_id, and content_type_id fields
• Resolve content links using PGVector and Django model introspection
• ✅ Added repair_embedding_links CLI command
• Reports total scanned, fixed, and skipped rows

Memory Context Propagation
• ✅ Updated create_memory_from_chunk() to:
• Infer the document.memory_context if missing using the first linked assistant
• Prevents future mismatches during chunk memory creation

Diagnostic Enhancements
• ✅ replay_rag_query now:
• Warns when no chunks are returned
• Supports --log-debug to show chunk count, memory context, and fallback reasons

⸻

🖥️ UI & API Additions

Embedding Debug Panel
• ✅ Shows broken embeddings count
• ✅ Displays assistants without document-linked chunks
• ✅ Red highlights for retrieval errors or missing contexts
• ✅ Full assistant → context → retrieval table for visual inspection

⸻

🧪 Tests Added
• Regression tests for:
• Embedding repair logic
• Chunk memory context propagation from assistant
• API response checks for /devtools/embedding-debug

⸻
