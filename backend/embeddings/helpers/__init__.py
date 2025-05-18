"""
Embeddings helper modules.
"""

try:
    from .helpers_io import (
        get_cache,
        set_cache,
        save_embedding,
        queue_for_processing,
        retrieve_embeddings,
        search_similar_embeddings,
        save_message,
        update_memory,
        retrieve_similar_messages,
        search_similar_embeddings_for_model,
        get_embedding_for_text,
    )
except Exception:
    # helpers_io may require Django cache or models; skip if not available
    pass
from .helpers_processing import (
    retry_with_backoff,
    generate_embedding,
    compute_similarity,
    find_similar_characters,
)

__all__ = [
    "get_cache",
    "set_cache",
    "save_embedding",
    "queue_for_processing",
    "retrieve_embeddings",
    "search_similar_embeddings",
    "save_message",
    "update_memory",
    "retrieve_similar_messages",
    "search_similar_embeddings_for_model",
    "get_embedding_for_text",
    "retry_with_backoff",
    "generate_embedding",
    "compute_similarity",
    "find_similar_characters",
]
