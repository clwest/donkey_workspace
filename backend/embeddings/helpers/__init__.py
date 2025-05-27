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
    # helpers_io may require Django cache or models; provide fallbacks
    def _na(*args, **kwargs):
        raise ImportError("embeddings.helpers_io unavailable")

    get_cache = set_cache = save_embedding = queue_for_processing = _na
    retrieve_embeddings = search_similar_embeddings = save_message = _na
    update_memory = retrieve_similar_messages = search_similar_embeddings_for_model = _na
    get_embedding_for_text = _na
try:
    from .helpers_processing import (
        retry_with_backoff,
        generate_embedding,
        compute_similarity,
        find_similar_characters,
    )
except Exception:
    def _na(*args, **kwargs):
        raise ImportError("embeddings.helpers_processing unavailable")

    retry_with_backoff = generate_embedding = compute_similarity = _na
    find_similar_characters = _na

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
