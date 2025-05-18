"""
Cache Service Module

This module provides a unified and robust caching service that works consistently
across different environments. It supports various backends (Redis, in-memory) with
fallback mechanisms and standardized error handling.
"""

import json
import logging
import time
import os
import threading
from typing import Any, Dict, Optional, List, Union, Tuple
from functools import wraps

# Configure logger
logger = logging.getLogger("django")

# Try to import Django's cache framework
try:
    from django.core.cache import cache as django_cache
    from django.conf import settings

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

# Try to import Redis
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class InMemoryCache:
    """Simple thread-safe in-memory cache implementation."""

    def __init__(self):
        """Initialize the in-memory cache."""
        self._cache = {}
        self._expiry = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Any:
        """
        Get a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            Any: The cached value or None if not found or expired
        """
        with self._lock:
            # Check if key exists and is not expired
            if key in self._cache:
                # Check expiration
                if key in self._expiry and self._expiry[key] < time.time():
                    # Expired, remove it
                    del self._cache[key]
                    del self._expiry[key]
                    return None
                return self._cache[key]
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            timeout (int, optional): Expiration time in seconds
        """
        with self._lock:
            self._cache[key] = value
            if timeout is not None:
                self._expiry[key] = time.time() + timeout

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key (str): Cache key
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]

    def clear(self) -> None:
        """Clear all values from the cache."""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from the cache.

        Args:
            keys (List[str]): List of cache keys

        Returns:
            Dict[str, Any]: Dictionary of found keys and their values
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> None:
        """
        Set multiple values in the cache.

        Args:
            data (Dict[str, Any]): Dictionary of key-value pairs
            timeout (int, optional): Expiration time in seconds
        """
        for key, value in data.items():
            self.set(key, value, timeout)

    def incr(self, key: str, delta: int = 1) -> int:
        """
        Increment a value in the cache.

        Args:
            key (str): Cache key
            delta (int): Amount to increment by

        Returns:
            int: New value

        Raises:
            ValueError: If the value cannot be incremented
        """
        with self._lock:
            value = self.get(key)
            if value is None:
                value = 0
            if not isinstance(value, (int, float)):
                raise ValueError(f"Cannot increment non-numeric value: {value}")
            new_value = value + delta
            self.set(key, new_value)
            return new_value


class RedisCache:
    """Redis-based cache implementation."""

    def __init__(
        self, host="localhost", port=6379, db=0, password=None, socket_timeout=None
    ):
        """
        Initialize the Redis cache.

        Args:
            host (str): Redis host
            port (int): Redis port
            db (int): Redis database number
            password (str, optional): Redis password
            socket_timeout (int, optional): Socket timeout
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "Redis is not available. Install with 'pip install redis'"
            )

        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            decode_responses=False,  # Keep binary data as is
        )

    def get(self, key: str) -> Any:
        """
        Get a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            Any: The cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"❌ Redis get error for key '{key}': {str(e)}")
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            serialized = self._serialize(value)
            if timeout is not None:
                return bool(self.client.setex(key, timeout, serialized))
            else:
                return bool(self.client.set(key, serialized))
        except Exception as e:
            logger.error(f"❌ Redis set error for key '{key}': {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"❌ Redis delete error for key '{key}': {str(e)}")
            return False

    def clear(self, pattern: str = "*") -> bool:
        """
        Clear all values matching pattern from the cache.

        Args:
            pattern (str): Pattern to match keys

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"❌ Redis clear error for pattern '{pattern}': {str(e)}")
            return False

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from the cache.

        Args:
            keys (List[str]): List of cache keys

        Returns:
            Dict[str, Any]: Dictionary of found keys and their values
        """
        try:
            pipe = self.client.pipeline()
            for key in keys:
                pipe.get(key)
            values = pipe.execute()

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            return result
        except Exception as e:
            logger.error(f"❌ Redis get_many error: {str(e)}")
            return {}

    def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """
        Set multiple values in the cache.

        Args:
            data (Dict[str, Any]): Dictionary of key-value pairs
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            pipe = self.client.pipeline()
            for key, value in data.items():
                serialized = self._serialize(value)
                if timeout is not None:
                    pipe.setex(key, timeout, serialized)
                else:
                    pipe.set(key, serialized)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"❌ Redis set_many error: {str(e)}")
            return False

    def incr(self, key: str, delta: int = 1) -> Optional[int]:
        """
        Increment a value in the cache.

        Args:
            key (str): Cache key
            delta (int): Amount to increment by

        Returns:
            int: New value, or None if operation failed
        """
        try:
            # Check if key exists
            if not self.client.exists(key):
                self.client.set(key, 0)

            if delta == 1:
                return self.client.incr(key)
            else:
                return self.client.incrby(key, delta)
        except Exception as e:
            logger.error(f"❌ Redis incr error for key '{key}': {str(e)}")
            return None

    def _serialize(self, value: Any) -> bytes:
        """
        Serialize a value for storage in Redis.

        Args:
            value (Any): Value to serialize

        Returns:
            bytes: Serialized value
        """
        import pickle

        try:
            return pickle.dumps(value)
        except Exception:
            # Fallback to JSON for basic types
            try:
                return json.dumps(value).encode("utf-8")
            except Exception as e:
                logger.error(f"❌ Serialization error: {str(e)}")
                return str(value).encode("utf-8")

    def _deserialize(self, value: bytes) -> Any:
        """
        Deserialize a value from Redis.

        Args:
            value (bytes): Value to deserialize

        Returns:
            Any: Deserialized value
        """
        import pickle

        try:
            return pickle.loads(value)
        except Exception:
            # Try JSON if pickle fails
            try:
                return json.loads(value.decode("utf-8"))
            except Exception:
                # Return as string if all else fails
                try:
                    return value.decode("utf-8")
                except Exception:
                    return value


class DjangoCache:
    """Django cache framework wrapper."""

    def __init__(self):
        """Initialize the Django cache wrapper."""
        if not DJANGO_AVAILABLE:
            raise ImportError("Django cache framework not available")

    def get(self, key: str) -> Any:
        """
        Get a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            Any: The cached value or None if not found
        """
        try:
            return django_cache.get(key)
        except Exception as e:
            logger.error(f"❌ Django cache get error for key '{key}': {str(e)}")
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            django_cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"❌ Django cache set error for key '{key}': {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            django_cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Django cache delete error for key '{key}': {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Clear all values from the cache.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            django_cache.clear()
            return True
        except Exception as e:
            logger.error(f"❌ Django cache clear error: {str(e)}")
            return False

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from the cache.

        Args:
            keys (List[str]): List of cache keys

        Returns:
            Dict[str, Any]: Dictionary of found keys and their values
        """
        try:
            return django_cache.get_many(keys)
        except Exception as e:
            logger.error(f"❌ Django cache get_many error: {str(e)}")
            return {}

    def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """
        Set multiple values in the cache.

        Args:
            data (Dict[str, Any]): Dictionary of key-value pairs
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            django_cache.set_many(data, timeout)
            return True
        except Exception as e:
            logger.error(f"❌ Django cache set_many error: {str(e)}")
            return False

    def incr(self, key: str, delta: int = 1) -> Optional[int]:
        """
        Increment a value in the cache.

        Args:
            key (str): Cache key
            delta (int): Amount to increment by

        Returns:
            int: New value, or None if operation failed
        """
        try:
            # Make sure the key exists
            if django_cache.get(key) is None:
                django_cache.set(key, 0)
            return django_cache.incr(key, delta)
        except Exception as e:
            logger.error(f"❌ Django cache incr error for key '{key}': {str(e)}")
            return None


class CacheService:
    """
    Unified cache service with fallback mechanisms.

    This service attempts to use the available cache backends in order:
    1. Django's cache framework (if available)
    2. Direct Redis connection (if available)
    3. In-memory cache (always available as final fallback)

    Configuration is read from environment variables or Django settings.
    """

    def __init__(self, force_backend=None):
        """
        Initialize the cache service.

        Args:
            force_backend (str, optional): Force a specific backend ('django', 'redis', or 'memory')
        """
        self.backends = []
        self._primary_backend = None

        # Default cache configuration
        self.config = {
            "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
            "REDIS_PORT": int(os.getenv("REDIS_PORT", 6379)),
            "REDIS_DB": int(os.getenv("REDIS_DB", 1)),
            "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD", None),
            "DEFAULT_TIMEOUT": int(os.getenv("CACHE_DEFAULT_TIMEOUT", 3600)),
            "PREFIX": os.getenv("CACHE_PREFIX", "donkeybetz:"),
        }

        # Override with Django settings if available
        if DJANGO_AVAILABLE:
            if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                cache_settings = settings.CACHES["default"]
                if (
                    "LOCATION" in cache_settings
                    and "redis://" in cache_settings["LOCATION"]
                ):
                    # Parse Redis URL
                    parts = (
                        cache_settings["LOCATION"].replace("redis://", "").split(":")
                    )
                    self.config["REDIS_HOST"] = parts[0]
                    port_db = parts[1].split("/")
                    self.config["REDIS_PORT"] = int(port_db[0])
                    if len(port_db) > 1:
                        self.config["REDIS_DB"] = int(port_db[1])

                if (
                    "OPTIONS" in cache_settings
                    and "PASSWORD" in cache_settings["OPTIONS"]
                ):
                    self.config["REDIS_PASSWORD"] = cache_settings["OPTIONS"][
                        "PASSWORD"
                    ]

        # Initialize backends based on availability or forced backend
        if force_backend:
            if force_backend == "django" and DJANGO_AVAILABLE:
                self._setup_django_backend()
            elif force_backend == "redis" and REDIS_AVAILABLE:
                self._setup_redis_backend()
            elif force_backend == "memory":
                self._setup_memory_backend()
            else:
                raise ValueError(f"Forced backend '{force_backend}' not available")
        else:
            # Try all backends in order of preference
            try:
                if DJANGO_AVAILABLE:
                    self._setup_django_backend()
            except Exception as e:
                logger.warning(f"⚠️ Django cache not available: {str(e)}")

            try:
                if REDIS_AVAILABLE and not self._primary_backend:
                    self._setup_redis_backend()
            except Exception as e:
                logger.warning(f"⚠️ Redis cache not available: {str(e)}")

            # Always set up in-memory as fallback
            if not self._primary_backend:
                self._setup_memory_backend()

        logger.info(
            f"✅ Cache service initialized with primary backend: {self._primary_backend.__class__.__name__}"
        )

    def _setup_django_backend(self):
        """Set up Django cache backend."""
        backend = DjangoCache()
        self.backends.insert(0, backend)
        if not self._primary_backend:
            self._primary_backend = backend

    def _setup_redis_backend(self):
        """Set up Redis cache backend."""
        backend = RedisCache(
            host=self.config["REDIS_HOST"],
            port=self.config["REDIS_PORT"],
            db=self.config["REDIS_DB"],
            password=self.config["REDIS_PASSWORD"],
        )
        self.backends.insert(0, backend)
        if not self._primary_backend:
            self._primary_backend = backend

    def _setup_memory_backend(self):
        """Set up in-memory cache backend."""
        backend = InMemoryCache()
        self.backends.append(backend)
        if not self._primary_backend:
            self._primary_backend = backend

    def _format_key(self, key: str) -> str:
        """
        Format a cache key with the configured prefix.

        Args:
            key (str): Original cache key

        Returns:
            str: Formatted cache key
        """
        if not key.startswith(self.config["PREFIX"]):
            return f"{self.config['PREFIX']}{key}"
        return key

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.

        Args:
            key (str): Cache key
            default (Any): Default value if key not found

        Returns:
            Any: The cached value or default if not found
        """
        formatted_key = self._format_key(key)

        # Try each backend in order
        for backend in self.backends:
            try:
                value = backend.get(formatted_key)
                if value is not None:
                    return value
            except Exception as e:
                logger.error(
                    f"❌ Cache get error with {backend.__class__.__name__}: {str(e)}"
                )

        return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key (str): Cache key
            value (Any): Value to cache
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if set in at least one backend
        """
        if timeout is None:
            timeout = self.config["DEFAULT_TIMEOUT"]

        formatted_key = self._format_key(key)
        success = False

        # Try to set in all backends
        for backend in self.backends:
            try:
                if backend.set(formatted_key, value, timeout):
                    success = True
            except Exception as e:
                logger.error(
                    f"❌ Cache set error with {backend.__class__.__name__}: {str(e)}"
                )

        return success

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            bool: True if deleted from at least one backend
        """
        formatted_key = self._format_key(key)
        success = False

        # Try to delete from all backends
        for backend in self.backends:
            try:
                if backend.delete(formatted_key):
                    success = True
            except Exception as e:
                logger.error(
                    f"❌ Cache delete error with {backend.__class__.__name__}: {str(e)}"
                )

        return success

    def clear(self, pattern: str = "*") -> bool:
        """
        Clear values from the cache.

        Args:
            pattern (str): Pattern to match keys (only used with Redis)

        Returns:
            bool: True if cleared from at least one backend
        """
        success = False

        # Try to clear all backends
        for backend in self.backends:
            try:
                if isinstance(backend, RedisCache):
                    if backend.clear(self._format_key(pattern)):
                        success = True
                else:
                    if backend.clear():
                        success = True
            except Exception as e:
                logger.error(
                    f"❌ Cache clear error with {backend.__class__.__name__}: {str(e)}"
                )

        return success

    def get_many(self, keys: List[str], default: Any = None) -> Dict[str, Any]:
        """
        Get multiple values from the cache.

        Args:
            keys (List[str]): List of cache keys
            default (Any): Default value for missing keys

        Returns:
            Dict[str, Any]: Dictionary of found keys and their values
        """
        formatted_keys = [self._format_key(key) for key in keys]
        result = {key: default for key in keys}

        # Try each backend in order
        for backend in self.backends:
            try:
                backend_result = backend.get_many(formatted_keys)

                # Convert formatted keys back to original keys
                for i, formatted_key in enumerate(formatted_keys):
                    if formatted_key in backend_result:
                        orig_key = keys[i]
                        result[orig_key] = backend_result[formatted_key]

                # If we got all keys, we can stop
                if all(value is not default for value in result.values()):
                    break
            except Exception as e:
                logger.error(
                    f"❌ Cache get_many error with {backend.__class__.__name__}: {str(e)}"
                )

        return result

    def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """
        Set multiple values in the cache.

        Args:
            data (Dict[str, Any]): Dictionary of key-value pairs
            timeout (int, optional): Expiration time in seconds

        Returns:
            bool: True if set in at least one backend
        """
        if timeout is None:
            timeout = self.config["DEFAULT_TIMEOUT"]

        formatted_data = {self._format_key(key): value for key, value in data.items()}
        success = False

        # Try to set in all backends
        for backend in self.backends:
            try:
                if backend.set_many(formatted_data, timeout):
                    success = True
            except Exception as e:
                logger.error(
                    f"❌ Cache set_many error with {backend.__class__.__name__}: {str(e)}"
                )

        return success

    def incr(self, key: str, delta: int = 1) -> Optional[int]:
        """
        Increment a value in the cache.

        Args:
            key (str): Cache key
            delta (int): Amount to increment by

        Returns:
            int: New value, or None if operation failed in all backends
        """
        formatted_key = self._format_key(key)

        # Try the primary backend first for consistency
        try:
            result = self._primary_backend.incr(formatted_key, delta)
            if result is not None:
                return result
        except Exception as e:
            logger.error(f"❌ Primary cache incr error: {str(e)}")

        # Try other backends
        for backend in self.backends:
            if backend is not self._primary_backend:
                try:
                    result = backend.incr(formatted_key, delta)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.error(
                        f"❌ Cache incr error with {backend.__class__.__name__}: {str(e)}"
                    )

        return None

    def cached(self, timeout: Optional[int] = None, key_prefix: str = "", key_fn=None):
        """
        Decorator to cache function results.

        Args:
            timeout (int, optional): Cache timeout in seconds
            key_prefix (str): Prefix for cache key
            key_fn (callable, optional): Function to generate cache key

        Returns:
            callable: Decorated function
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_fn:
                    key = key_fn(*args, **kwargs)
                else:
                    # Default key based on function name and arguments
                    key_parts = [func.__module__, func.__name__]
                    # Add stringified args and kwargs
                    for arg in args:
                        key_parts.append(str(arg))
                    for k, v in sorted(kwargs.items()):
                        key_parts.append(f"{k}:{v}")
                    key = key_prefix + ":" + ":".join(key_parts)

                # Try to get from cache
                cached_result = self.get(key)
                if cached_result is not None:
                    return cached_result

                # Call the function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, timeout)
                return result

            return wrapper

        return decorator

    def memoize(self, timeout: Optional[int] = None):
        """
        Decorator to memoize function results by arguments.

        This is a simpler version of the cached decorator that
        creates keys based solely on the function and its args.

        Args:
            timeout (int, optional): Cache timeout in seconds

        Returns:
            callable: Decorated function
        """
        return self.cached(timeout=timeout)


# Singleton instance
_cache_service = None


def get_cache_service(force_backend=None) -> CacheService:
    """
    Get or create the cache service singleton.

    Args:
        force_backend (str, optional): Force a specific backend

    Returns:
        CacheService: The cache service instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService(force_backend=force_backend)
    return _cache_service


# Convenience functions that use the singleton
def get_cache(key: str, default: Any = None) -> Any:
    """Get a value from the cache."""
    return get_cache_service().get(key, default)


def set_cache(key: str, value: Any, timeout: Optional[int] = None) -> bool:
    """Set a value in the cache."""
    return get_cache_service().set(key, value, timeout)


def delete_cache(key: str) -> bool:
    """Delete a value from the cache."""
    return get_cache_service().delete(key)


def clear_cache(pattern: str = "*") -> bool:
    """Clear the cache."""
    return get_cache_service().clear(pattern)


def get_many_cache(keys: List[str], default: Any = None) -> Dict[str, Any]:
    """Get multiple values from the cache."""
    return get_cache_service().get_many(keys, default)


def set_many_cache(data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
    """Set multiple values in the cache."""
    return get_cache_service().set_many(data, timeout)


def incr_cache(key: str, delta: int = 1) -> Optional[int]:
    """Increment a value in the cache."""
    return get_cache_service().incr(key, delta)


def cached(timeout: Optional[int] = None, key_prefix: str = "", key_fn=None):
    """Decorator to cache function results."""
    return get_cache_service().cached(timeout, key_prefix, key_fn)


def memoize(timeout: Optional[int] = None):
    """Decorator to memoize function results."""
    return get_cache_service().memoize(timeout)
