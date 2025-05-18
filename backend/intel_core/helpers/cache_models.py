_MODEL_CACHE = {}


def get_cached_model(name):
    return _MODEL_CACHE.get(name)


def cache_model(name, instance):
    _MODEL_CACHE[name] = instance
    return True


# 🔹 helpers/cache_user.py
from .cache_core import get_cache, set_cache, delete_cache


def get_user_context(user_id, context_key):
    return get_cache(f"user:{user_id}:{context_key}")


def store_user_context(user_id, context_key, data, ttl=3600):
    return set_cache(f"user:{user_id}:{context_key}", data, ttl)


def clear_user_context(user_id, context_key=None):
    if context_key:
        return delete_cache(f"user:{user_id}:{context_key}")
    return False  # for full-clear we’d need key pattern delete support
