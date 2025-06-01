"""
Cache utilities for optimizing vector searches and AI responses.
Implements intelligent caching with Redis for frequently accessed data.
"""

import json
import hashlib
import pickle
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import numpy as np
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Cache timeouts (in seconds)
VECTOR_CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours
CHATBOT_CACHE_TIMEOUT = 60 * 30  # 30 minutes
EMBEDDING_CACHE_TIMEOUT = 60 * 60  # 1 hour


class VectorCache:
    """Handles caching of vector embeddings and similarity search results."""

    @staticmethod
    def get_vector_key(text: str, model_name: str) -> str:
        """Generate a cache key for vector embeddings."""
        text_hash = hashlib.md5(text.encode(errors="ignore")).hexdigest()
        return f"vector:{model_name}:{text_hash}"

    @staticmethod
    def get_similarity_key(query_vector: np.ndarray, collection_id: str) -> str:
        """Generate a cache key for similarity search results."""
        vector_hash = hashlib.md5(query_vector.tobytes()).hexdigest()
        return f"similarity:{collection_id}:{vector_hash}"

    @classmethod
    def cache_vector(cls, text: str, vector: np.ndarray, model_name: str) -> None:
        """Cache a vector embedding."""
        try:
            key = cls.get_vector_key(text, model_name)
            cache.set(key, pickle.dumps(vector), VECTOR_CACHE_TIMEOUT)
            logger.debug(f"Cached vector for text: {text[:50]}...")
        except Exception as e:
            logger.error(f"Error caching vector: {str(e)}")

    @classmethod
    def get_cached_vector(cls, text: str, model_name: str) -> Optional[np.ndarray]:
        """Retrieve a cached vector embedding."""
        try:
            key = cls.get_vector_key(text, model_name)
            cached = cache.get(key)
            if cached:
                return pickle.loads(cached)
        except Exception as e:
            logger.error(f"Error retrieving cached vector: {str(e)}")
        return None

    @classmethod
    def cache_similarity_results(
        cls,
        query_vector: np.ndarray,
        collection_id: str,
        results: List[Dict],
        timeout: int = VECTOR_CACHE_TIMEOUT,
    ) -> None:
        """Cache similarity search results."""
        try:
            key = cls.get_similarity_key(query_vector, collection_id)
            cache.set(key, json.dumps(results), timeout)
            logger.debug(f"Cached similarity results for collection: {collection_id}")
        except Exception as e:
            logger.error(f"Error caching similarity results: {str(e)}")

    @classmethod
    def get_cached_similarity(
        cls, query_vector: np.ndarray, collection_id: str
    ) -> Optional[List[Dict]]:
        """Retrieve cached similarity search results."""
        try:
            key = cls.get_similarity_key(query_vector, collection_id)
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error retrieving cached similarity results: {str(e)}")
        return None


class AIResponseCache:
    """Handles caching of AI-generated responses."""

    @staticmethod
    def get_response_key(prompt: str, model: str, temperature: float) -> str:
        """Generate a cache key for AI responses."""
        prompt_hash = hashlib.md5(prompt.encode(errors="ignore")).hexdigest()
        return f"ai_response:{model}:{temperature}:{prompt_hash}"

    @classmethod
    def cache_response(
        cls,
        prompt: str,
        response: str,
        model: str,
        temperature: float,
        timeout: int = CHATBOT_CACHE_TIMEOUT,
    ) -> None:
        """Cache an AI-generated response."""
        try:
            key = cls.get_response_key(prompt, model, temperature)
            cache.set(key, response, timeout)
            logger.debug(f"Cached AI response for prompt: {prompt[:50]}...")
        except Exception as e:
            logger.error(f"Error caching AI response: {str(e)}")

    @classmethod
    def get_cached_response(
        cls, prompt: str, model: str, temperature: float
    ) -> Optional[str]:
        """Retrieve a cached AI response."""
        try:
            key = cls.get_response_key(prompt, model, temperature)
            return cache.get(key)
        except Exception as e:
            logger.error(f"Error retrieving cached AI response: {str(e)}")
        return None


class MemoryCache:
    """Handles caching of AI conversation memory."""

    @staticmethod
    def get_memory_key(session_id: str, memory_type: str) -> str:
        """Generate a cache key for conversation memory."""
        return f"memory:{memory_type}:{session_id}"

    @classmethod
    def cache_short_term_memory(
        cls, session_id: str, memory: Dict, timeout: int = CHATBOT_CACHE_TIMEOUT
    ) -> None:
        """Cache short-term conversation memory."""
        try:
            key = cls.get_memory_key(session_id, "short_term")
            cache.set(key, json.dumps(memory), timeout)
            logger.debug(f"Cached short-term memory for session: {session_id}")
        except Exception as e:
            logger.error(f"Error caching short-term memory: {str(e)}")

    @classmethod
    def get_cached_short_term_memory(cls, session_id: str) -> Optional[Dict]:
        """Retrieve cached short-term memory.

        Returns a ``dict`` if present, otherwise ``None``.
        """
        try:
            key = cls.get_memory_key(session_id, "short_term")
            cached = cache.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error retrieving short-term memory: {str(e)}")
        return None

    @classmethod
    def invalidate_memory(cls, session_id: str) -> None:
        """Invalidate all memory caches for a session."""
        try:
            short_term_key = cls.get_memory_key(session_id, "short_term")
            cache.delete(short_term_key)
            logger.debug(f"Invalidated memory cache for session: {session_id}")
        except Exception as e:
            logger.error(f"Error invalidating memory cache: {str(e)}")


def clear_expired_caches() -> None:
    """Clear expired caches to prevent memory bloat."""
    try:
        # Note: Redis handles expiration automatically
        # This is just for logging and monitoring
        logger.info("Redis cache cleanup completed")
    except Exception as e:
        logger.error(f"Error during cache cleanup: {str(e)}")


def monitor_cache_size() -> Dict[str, int]:
    """Monitor Redis cache size and usage."""
    try:
        info = cache.client.info()
        return {
            "used_memory": info["used_memory"],
            "used_memory_peak": info["used_memory_peak"],
            "total_keys": info["total_keys"] if "total_keys" in info else 0,
        }
    except Exception as e:
        logger.error(f"Error monitoring cache size: {str(e)}")
        return {}
