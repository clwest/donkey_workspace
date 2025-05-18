"""
document_caching.py

Redis-backed caching for document embeddings and session tracking.
"""

import logging
import json
from typing import List, Optional
from django.core.cache import cache

logger = logging.getLogger("embeddings")

# Time-to-live settings
DOC_TTL = 60 * 60 * 24  # 24 hours
SESSION_TTL = 60 * 60 * 24  # 24 hours

__all__ = [
    "cache_document_embedding",
    "get_cached_embedding",
    "track_session_usage",
    "get_session_docs",
]


def cache_document_embedding(doc_id: str, embedding: List[float]) -> None:
    """
    Cache a document-level embedding in Redis.

    Args:
        doc_id: Identifier of the document.
        embedding: Embedding vector as a list of floats.
    """
    key = f"doc:{doc_id}:embedding"
    try:
        cache.set(key, json.dumps(embedding), timeout=DOC_TTL)
    except Exception as e:
        logger.error(f"Error caching embedding for doc {doc_id}: {e}", exc_info=True)


def get_cached_embedding(doc_id: str) -> Optional[List[float]]:
    """
    Retrieve a cached document embedding from Redis.

    Args:
        doc_id: Identifier of the document.

    Returns:
        The embedding as a list of floats, or None if not found or on error.
    """
    key = f"doc:{doc_id}:embedding"
    try:
        raw = cache.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.error(
            f"Error retrieving cached embedding for doc {doc_id}: {e}", exc_info=True
        )
        return None


def track_session_usage(session_id: str, doc_id: str) -> None:
    """
    Track that a document was processed in a session.

    Args:
        session_id: Identifier of the session.
        doc_id: Identifier of the document.
    """
    key = f"session:{session_id}:docs"
    try:
        raw = cache.get(key)
        if raw:
            docs = json.loads(raw)
            if doc_id not in docs:
                docs.append(doc_id)
        else:
            docs = [doc_id]
        cache.set(key, json.dumps(docs), timeout=SESSION_TTL)
    except Exception as e:
        logger.error(
            f"Error tracking session {session_id} usage for doc {doc_id}: {e}",
            exc_info=True,
        )


def get_session_docs(session_id: str) -> List[str]:
    """
    Retrieve the list of document IDs processed in a session.

    Args:
        session_id: Identifier of the session.

    Returns:
        List of document IDs, or empty list if none found.
    """
    key = f"session:{session_id}:docs"
    try:
        raw = cache.get(key)
        if not raw:
            return []
        return json.loads(raw)
    except Exception as e:
        logger.error(
            f"Error retrieving session docs for session {session_id}: {e}",
            exc_info=True,
        )
        return []
