"""helpers_processing.py

Embedding generation, retry logic, and processing utilities.

Public helper functions:
- ``retry_with_backoff``
- ``generate_embedding``
- ``compute_similarity``
- ``find_similar_characters``
"""

# Standard libraries
import time
import random
import logging
import math
import tiktoken

# OpenAI client for v1.x SDK
from openai import OpenAI
from prompts.utils.token_helpers import EMBEDDING_MODEL

MAX_TOKENS = 8192
tokenizer = tiktoken.encoding_for_model(EMBEDDING_MODEL)

__all__ = [
    "retry_with_backoff",
    "generate_embedding",
    "compute_similarity",
    "find_similar_characters",
]

# PGVector availability flag for potential DB-side similarity
try:
    from pgvector.django import CosineDistance

    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
from typing import Any, Callable, Dict, List, Optional
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger("embeddings")

# Initialize OpenAI client (expects OPENAI_API_KEY in env)
client = OpenAI()


def retry_with_backoff(
    func: Callable[..., Any],
    *args: Any,
    retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """
    Retry a function with exponential backoff and jitter.
    Raises the last exception if all retries fail.
    """
    attempt = 0
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            attempt += 1
            if attempt > retries:
                logger.error(
                    f"Function {func.__name__} failed after {retries} retries: {e}",
                    exc_info=True,
                )
                raise
            delay = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0, delay * 0.1)
            sleep_time = delay + jitter
            logger.warning(
                f"Retry {attempt}/{retries} for {func.__name__} after {sleep_time:.2f}s: {e}"
            )
            time.sleep(sleep_time)


def generate_embedding(
    text: str, model: str = EMBEDDING_MODEL
) -> Optional[List[float]]:
    """
    Generate embeddings for the given text using OpenAI's API.

    Args:
        text: Input string to embed.
        model: The OpenAI embedding model to use.

    Returns:
        A list of floats representing the embedding, or None on failure.
    """
    if not text or not text.strip():
        logger.warning("Empty or blank text provided to generate_embedding.")
        return None
    
    tokens = tokenizer.encode(text)
    if len(tokens) > MAX_TOKENS:
        tokens = tokens[:MAX_TOKENS]
        text = tokenizer.decode(tokens)
    try:
        # Generate embedding via OpenAI v1.x SDK
        response = retry_with_backoff(
            client.embeddings.create,
            input=text,
            model=model,
        )
        # Extract embedding vector
        data_list = getattr(response, "data", None) or response.get("data", [])
        if not data_list or (
            not hasattr(data_list[0], "embedding") and "embedding" not in data_list[0]
        ):
            logger.error(f"No embedding in response: {response}")
            return []
        embedding = (
            data_list[0].embedding
            if hasattr(data_list[0], "embedding")
            else data_list[0]["embedding"]
        )
        if not isinstance(embedding, list):
            logger.error(f"Unexpected embedding type: {type(embedding)}")
            return []
        return embedding
    except Exception as e:
        logger.error(f"❌ Error generating embedding: {e}", exc_info=True)
        return []




def find_similar_characters(
    vector: List[float], top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Find top_k characters whose training embeddings are most similar to the input vector.

    Uses PGVector database cosine similarity if available, otherwise falls back to manual computation.

    Args:
        vector: Query embedding vector.
        top_k: Number of top results to return.

    Returns:
        List of dicts with keys: 'id', 'name', 'score'.
    """
    results: List[Dict[str, Any]] = []
    try:
        from characters.models import CharacterTrainingProfile

        # Database-side similarity via pgvector is not supported for JSONField embeddings
        # Always fallback to manual computation
        # Fallback: manual computation
        all_profiles = CharacterTrainingProfile.objects.filter(
            status="complete"
        ).exclude(embedding__isnull=True)
        for tp in all_profiles:
            try:
                score = compute_similarity(vector, tp.embedding)
                results.append(
                    {
                        "id": tp.character.id,
                        "name": tp.character.name,
                        "score": score,
                    }
                )
            except Exception:
                continue
        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    except ImportError:
        logger.error(
            "characters.models not available; cannot perform similarity search."
        )
        return []
