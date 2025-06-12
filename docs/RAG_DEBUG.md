# RAG Debug Summary

This document tracks repair operations for RAG chunk retrieval.

- `repair_rag_chunk_links` fixes missing document context links and invalid embedding references.
- `embedding-debug` panel now shows retrieval counts per assistant when toggled.

Run `python manage.py repair_rag_chunk_links` after seeding to ensure all links are valid.
