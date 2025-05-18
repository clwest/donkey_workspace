"""
Cache Helpers for Donkey Betz

This module provides convenience functions for caching data across the application.
It leverages the robust CacheService implementation with fallback mechanisms.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from django.core.cache import cache
from assistants.models import Assistant

# Configure logger
logger = logging.getLogger("django")

# Global model cache dictionary for in-memory caching
# This will persist across requests but within the same server process
_MODEL_CACHE = {}

# Import the improved cache service
from utils.cache_service import (
    get_cache,
    set_cache,
    delete_cache,
    clear_cache,
    get_many_cache as get_many,
    set_many_cache as set_many,
    incr_cache as incr,
    cached,
    memoize,
)


### 🔹 MODEL CACHING 🔹 ###
def get_cached_model(model_name):
    """
    Get a cached model instance from memory for faster repeated access.

    Args:
        model_name (str): The name/identifier of the model

    Returns:
        The cached model or None if not found
    """
    if model_name in _MODEL_CACHE:
        logger.info(f"✅ Using in-memory cached model: {model_name}")
        return _MODEL_CACHE[model_name]
    return None


def cache_model(model_name, model_instance):
    """
    Cache a model instance in memory for faster repeated access.

    Args:
        model_name (str): The name/identifier of the model
        model_instance: The model instance to cache

    Returns:
        bool: True if successful
    """
    try:
        _MODEL_CACHE[model_name] = model_instance
        logger.info(f"✅ Cached model in memory: {model_name}")
        return True
    except Exception as e:
        logger.error(f"❌ Error caching model: {str(e)}")
        return False


### 🔹 GENERAL CACHING 🔹 ###
def get_cache(key):
    """
    Get data from the cache using the provided key.

    Args:
        key (str): The cache key to retrieve

    Returns:
        The cached data or None if not found
    """
    try:
        cached_data = cache.get(key)
        if cached_data:
            logger.info(f"✅ Cache hit for key: {key}")
        else:
            logger.info(f"⚠️ Cache miss for key: {key}")
        return cached_data
    except Exception as e:
        logger.error(f"❌ Error retrieving from cache: {str(e)}")
        return None


def set_cache(key, data, timeout=3600):
    """
    Store data in the cache with the provided key.

    Args:
        key (str): The cache key to use
        data: The data to cache
        timeout (int): Expiration time in seconds (default 1 hour)

    Returns:
        bool: True if successful
    """
    try:
        cache.set(key, data, timeout=timeout)
        logger.info(f"✅ Cached data with key: {key}, expires in {timeout}s")
        return True
    except Exception as e:
        logger.error(f"❌ Error caching data: {str(e)}")
        return False


def clear_cache(key=None):
    """
    Clear the cache for a specific key or the entire cache.

    Args:
        key (str, optional): Specific key to clear. If None, clears entire cache.
    """
    if key:
        cache.delete(key)
        logger.info(f"🗑 Cleared cache for key: {key}")
    else:
        cache.clear()
        logger.info("🗑 Cleared entire cache")


### 🔹 USER MEMORY CACHING 🔹 ###
def get_cached_user_memory(user):
    """
    Retrieves user memory from cache, or fetches it from the database if missing.
    """
    cache_key = f"user_memory_{user.username}"
    cached_memory = get_cache(cache_key)

    if not cached_memory:
        logger.warning(f"⚠️ Cache miss for {user.username}. Fetching from database...")
        cached_memory = list(
            ChatMemory.objects.filter(user=user).values("memory_key", "memory_value")
        )

        # ✅ Store fetched memory in cache for future use
        set_cache(cache_key, cached_memory)

    return cached_memory


def update_user_memory_cache(user, memory):
    """Update the cache with fresh user memory data."""
    cache_key = f"user_memory_{user.username}"
    set_cache(cache_key, memory)
    logger.info(f"✅ Updated cache for {user.username}")


def invalidate_user_memory_cache(user):
    """Clear the user's cached memory."""
    cache_key = f"user_memory_{user.username}"
    clear_cache(cache_key)
    logger.info(f"🗑 Cleared memory cache for {user.username}")


### 🔹 SESSION CACHING 🔹 ###
def get_cached_session(session_id):
    """Retrieve cached session context if available."""
    cache_key = f"context_{session_id}"
    return get_cache(cache_key)


def update_session_cache(session_id, context_messages):
    """Cache session context for faster retrieval."""
    cache_key = f"context_{session_id}"
    set_cache(cache_key, context_messages, timeout=600)
    logger.info(f"✅ Cached session {session_id} context")


def invalidate_session_cache(session_id):
    """Remove session context from cache."""
    cache_key = f"context_{session_id}"
    clear_cache(cache_key)
    logger.info(f"🗑 Cleared cache for session {session_id}")


### 🔹 SESSION MEMORY MANAGEMENT 🔹 ###
def update_session_memory(session, key, value):
    """
    Updates or creates a memory entry for a session, avoiding duplicate key violations.

    Args:
        session (ChatSession): The session to update memory for
        key (str): The memory key
        value (str): The memory value

    Returns:
        ChatMemory: The created or updated memory object, or None if error
    """
    try:
        memory, created = ChatMemory.objects.update_or_create(
            session=session, memory_key=key, defaults={"memory_value": value}
        )
        return memory
    except Exception as e:
        logger.warning(f"⚠️ Error updating session memory: {str(e)}")
        return None


def store_context_metadata(session_id, context_data):
    """
    Store context metadata in the database.

    Args:
        session_id (str): The session ID
        context_data (dict): The context data to store

    Returns:
        bool: True if successful
    """
    try:
        from chatbots.models import ChatMemory, ChatSession
        from django.db import IntegrityError
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Get the session
        try:
            session = ChatSession.objects.get(session_id=session_id)
            user = session.user

            # If no user is associated with the session, use or create a system user
            if not user:
                user, created = User.objects.get_or_create(
                    username="system",
                    defaults={
                        "email": "system@donkeybetz.com",
                        "is_active": True,
                        "is_staff": False,
                        "is_superuser": False,
                    },
                )
                # Update the session with the system user
                session.user = user
                session.save(update_fields=["user"])
                logger.info(f"✅ Associated system user with session {session_id}")

        except ChatSession.DoesNotExist:
            logger.error(f"⚠️ Session {session_id} does not exist")
            return False

        # Check if a record already exists
        try:
            memory = ChatMemory.objects.get(
                session=session, user=user, memory_key="last_conversation_context"
            )

            # Update the existing record
            memory.memory_value = context_data
            memory.save()
            logger.info(f"✅ Updated context metadata for session {session_id}")
            return True

        except ChatMemory.DoesNotExist:
            # Create a new record
            try:
                ChatMemory.objects.create(
                    session=session,
                    user=user,
                    memory_key="last_conversation_context",
                    memory_value=context_data,
                )
                logger.info(f"✅ Created context metadata for session {session_id}")
                return True
            except IntegrityError as e:
                # Handle race condition - another process might have created the record
                memory = ChatMemory.objects.get(
                    session=session, user=user, memory_key="last_conversation_context"
                )
                memory.memory_value = context_data
                memory.save()
                logger.info(
                    f"✅ Handled race condition for context metadata, session {session_id}"
                )
                return True

    except Exception as e:
        logger.error(f"⚠️ Error storing context metadata: {str(e)}")
        return False


### 🔹 CONTEXT CACHING 🔹 ###
def store_user_context(
    user_id: str, context_key: str, context_data: Any, ttl: int = 3600
):
    """
    Store user-specific context in the cache.

    Args:
        user_id (str): User identifier
        context_key (str): Context identifier
        context_data (Any): Data to store
        ttl (int): Time-to-live in seconds (default: 1 hour)

    Returns:
        bool: True if successful
    """
    cache_key = f"user:{user_id}:{context_key}"
    return set_cache(cache_key, context_data, ttl)


def get_user_context(user_id: str, context_key: str):
    """
    Retrieve user-specific context from the cache.

    Args:
        user_id (str): User identifier
        context_key (str): Context identifier

    Returns:
        Any: The stored context data or None if not found
    """
    cache_key = f"user:{user_id}:{context_key}"
    return get_cache(cache_key)


def clear_user_context(user_id: str, context_key: str = None):
    """
    Clear user-specific context from the cache.

    Args:
        user_id (str): User identifier
        context_key (str, optional): Specific context key to clear, or None to clear all

    Returns:
        bool: True if successful
    """
    if context_key:
        # Clear specific context
        cache_key = f"user:{user_id}:{context_key}"
        return delete_cache(cache_key)
    else:
        # Clear all user context
        pattern = f"user:{user_id}:*"
        return clear_cache(pattern)


### 🔹 SESSION CACHING 🔹 ###
def store_session_data(session_id: str, key: str, data: Any, ttl: int = 1800):
    """
    Store session-specific data in the cache.

    Args:
        session_id (str): Session identifier
        key (str): Data key
        data (Any): Data to store
        ttl (int): Time-to-live in seconds (default: 30 minutes)

    Returns:
        bool: True if successful
    """
    cache_key = f"session:{session_id}:{key}"
    return set_cache(cache_key, data, ttl)


def get_session_data(session_id: str, key: str):
    """
    Retrieve session-specific data from the cache.

    Args:
        session_id (str): Session identifier
        key (str): Data key

    Returns:
        Any: The stored data or None if not found
    """
    cache_key = f"session:{session_id}:{key}"
    return get_cache(cache_key)


def clear_session_data(session_id: str, key: str = None):
    """
    Clear session-specific data from the cache.

    Args:
        session_id (str): Session identifier
        key (str, optional): Specific data key to clear, or None to clear all session data

    Returns:
        bool: True if successful
    """
    if key:
        # Clear specific data
        cache_key = f"session:{session_id}:{key}"
        return delete_cache(cache_key)
    else:
        # Clear all session data
        pattern = f"session:{session_id}:*"
        return clear_cache(pattern)


### 🔹 RATE LIMITING 🔹 ###
def increment_request_count(user_id: str, endpoint: str, window: int = 60):
    """
    Increment request count for rate limiting.

    Args:
        user_id (str): User identifier
        endpoint (str): API endpoint
        window (int): Time window in seconds (default: 60 seconds)

    Returns:
        int: Updated request count
    """
    cache_key = f"ratelimit:{user_id}:{endpoint}:{int(time.time() / window)}"
    count = incr_cache(cache_key, 1)
    if count is not None:
        # Set expiration if this is the first request in the window
        if count == 1:
            set_cache(cache_key, 1, window * 2)  # Set TTL to 2x window for safe overlap
        return count
    return 1  # Return 1 if increment failed


def get_request_count(user_id: str, endpoint: str, window: int = 60):
    """
    Get current request count for rate limiting.

    Args:
        user_id (str): User identifier
        endpoint (str): API endpoint
        window (int): Time window in seconds (default: 60 seconds)

    Returns:
        int: Current request count
    """
    cache_key = f"ratelimit:{user_id}:{endpoint}:{int(time.time() / window)}"
    count = get_cache(cache_key, 0)
    return count


### 🔹 API RESULT CACHING 🔹 ###
def cache_api_result(
    api_name: str, query_params: Dict[str, Any], result: Any, ttl: int = 3600
):
    """
    Cache API call results.

    Args:
        api_name (str): Name of the API
        query_params (Dict[str, Any]): Query parameters
        result (Any): API response to cache
        ttl (int): Time-to-live in seconds (default: 1 hour)

    Returns:
        bool: True if successful
    """
    # Sort query params to ensure consistent ordering
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))
    cache_key = f"api:{api_name}:{sorted_params}"
    return set_cache(cache_key, result, ttl)


def get_cached_api_result(api_name: str, query_params: Dict[str, Any]):
    """
    Get cached API call results.

    Args:
        api_name (str): Name of the API
        query_params (Dict[str, Any]): Query parameters

    Returns:
        Any: Cached API response or None if not found
    """
    # Sort query params to ensure consistent ordering
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(query_params.items()))
    cache_key = f"api:{api_name}:{sorted_params}"
    return get_cache(cache_key)


### 🔹 DECORATORS 🔹 ###
# The cached and memoize decorators are imported directly from cache_service
