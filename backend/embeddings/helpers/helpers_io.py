"""helpers_io.py

Embedding input/output and caching utilities.

Public helper functions:
- ``get_cache``
- ``set_cache``
- ``save_embedding``
- ``queue_for_processing``
- ``retrieve_embeddings``
- ``search_similar_embeddings``
- ``save_message``
- ``update_memory``
- ``retrieve_similar_messages``
- ``search_similar_embeddings_for_model``
- ``get_embedding_for_text``
"""

try:
    from embeddings.models import Embedding
    from django.contrib.contenttypes.models import ContentType
    from prompts.utils.token_helpers import EMBEDDING_MODEL
except Exception:  # pragma: no cover - likely missing Django
    Embedding = None
    ContentType = None
    EMBEDDING_MODEL = "text-embedding-3-small"
try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency may be absent
    OpenAI = None
from django.db.models import Q

try:
    from embeddings.vector_utils import compute_similarity
except Exception:  # pragma: no cover - optional dependency
    compute_similarity = None
import logging
from typing import Any, Optional, List, Tuple, Union, Dict
import uuid

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
]

# numpy not required in this module
try:
    import numpy as np
except ImportError:
    np = None
from django.core.cache import cache

logger = logging.getLogger("embeddings")

client = OpenAI() if OpenAI else None


# Caching utilities
def get_cache(key: str) -> Any:
    """Get a value from the cache."""
    try:
        return cache.get(key)
    except Exception as e:
        logger.error(f"Error getting cache for key {key}: {e}", exc_info=True)
        return None


def set_cache(key: str, value: Any, timeout: int = 3600) -> None:
    """Set a value in the cache."""
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {e}", exc_info=True)


# Asynchronous embedding save utilities
from embeddings.models import Embedding


from uuid import UUID


def save_embedding(
    obj: Any, embedding: List[float], session_id: Optional[UUID] = None
) -> Optional[Embedding]:
    """
    Save a vector embedding for a model instance using a GenericForeignKey.
    """
    try:
        if not embedding or not isinstance(embedding, list) or len(embedding) == 0:
            logger.warning(f"❌ Skipping embedding for {obj} — empty or invalid vector")
            return None

        if hasattr(obj, "_meta"):
            # Standard Django model instance
            content_type = ContentType.objects.get_for_model(obj.__class__)
            object_id = obj.id
            content = getattr(obj, "event", None) or str(obj)
        else:
            # Support lightweight objects (e.g., SimpleNamespace) with
            # `content_type` and `id` attributes.
            ct_name = getattr(obj, "content_type", None)
            object_id = getattr(obj, "id", None)

            if not ct_name or object_id is None:
                logger.error(
                    "save_embedding requires `content_type` and `id` attributes when a non-model object is provided"
                )
                return None

            # Support content_type names using underscores by stripping them for
            # comparison against Django's ``ContentType.model`` which does not
            # include underscores (e.g. ``DocumentChunk`` -> ``documentchunk``).
            normalized = ct_name.replace("_", "").lower() if ct_name else None
            content_type = ContentType.objects.filter(model=normalized).first()
            if not content_type:
                logger.error(f"Unknown content_type '{ct_name}' for {obj}")
                return None

            content = str(obj)

        emb = Embedding.objects.create(
            content_type=content_type,
            object_id=str(object_id) if object_id is not None else None,
            content_id=str(object_id),
            content=content,
            embedding=embedding,
            session_id=session_id,
        )
        return emb

    except Exception as e:
        logger.error(f"Error saving embedding for object {obj}: {e}", exc_info=True)
        return None


def queue_for_processing(
    text: str, content_type: str, content_id: str, model: str = "openai"
) -> None:
    """
    Simulate background queue logic for embedding generation.

    Args:
        text: The input text to embed.
        content_type: Type of content (e.g., 'document', 'chat_message').
        content_id: Identifier of the content.
        model: Embedding model identifier.
    """
    try:
        # Log the queue request; replace with Celery task in production
        logger.info(
            f"Queued embedding for processing: model={model}, "
            f"content_type={content_type}, content_id={content_id}, "
            f"text_length={len(text)}"
        )
    except Exception as e:
        logger.error(f"Error queueing embedding for processing: {e}", exc_info=True)


def retrieve_embeddings(content_type: str, content_ids: List[str]) -> List[Embedding]:
    """
    Fetch embeddings for the given content_type and list of content_ids.

    Args:
        content_type: Type of content (e.g., 'document', 'chat_message').
        content_ids: List of content_id strings.

    Returns:
        List of Embedding instances.
    """
    try:
        qs = Embedding.objects.filter(
            content_type=content_type, content_id__in=content_ids
        )
        return list(qs)
    except Exception as e:
        logger.error(
            f"Error retrieving embeddings for content_type={content_type}, "
            f"content_ids={content_ids}: {e}",
            exc_info=True,
        )
        return []


def search_similar_embeddings_for_model(
    query_vector: List[float],
    model_class,
    vector_field_name: str = "embedding",
    content_field_name: str = "content",
    top_k: int = 5,
    filters: Optional[Q] = None,
) -> List[Dict[str, Any]]:
    """
    Generic embedding search across any model with a vector field.

    Args:
        query_vector: The embedding vector to compare against.
        model_class: The Django model to search.
        vector_field_name: The name of the vector field (default 'embedding').
        content_field_name: The name of the field to return for display (default 'content').
        top_k: Number of top results to return.
        filters: Optional Q object to filter the queryset before comparison.

    Returns:
        List of dicts with id, content, and similarity score.
    """
    results = []
    try:
        qs = model_class.objects.exclude(**{f"{vector_field_name}__isnull": True})
        if filters:
            qs = qs.filter(filters)

        for obj in qs:
            try:
                vector = getattr(obj, vector_field_name)
                content = getattr(obj, content_field_name, str(obj))
                score = (
                    compute_similarity(query_vector, vector)
                    if compute_similarity
                    else 0.0
                )
                results.append(
                    {
                        "id": str(obj.id),
                        "content": content,
                        "score": score,
                    }
                )
            except Exception as e:
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    except Exception as e:
        logger.error(f"Embedding similarity search failed: {e}", exc_info=True)
        return []


def get_embedding_for_text(text: str) -> list[float]:
    if client is None:
        logger.error("OpenAI library not available; cannot fetch embedding.")
        return []

    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding
