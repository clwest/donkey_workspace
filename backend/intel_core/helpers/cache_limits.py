from .cache_core import get_cache, set_cache, incr_cache
from django.core.cache import cache
import time


def incr_cache(key, amount=1):
    try:
        return cache.incr(key, amount)
    except Exception:
        cache.set(key, amount)
        return amount


def increment_request_count(user_id, endpoint, window=60):
    key = f"ratelimit:{user_id}:{endpoint}:{int(time.time() / window)}"
    count = incr_cache(key)
    if count == 1:
        set_cache(key, count, window * 2)
    return count


def get_request_count(user_id, endpoint, window=60):
    key = f"ratelimit:{user_id}:{endpoint}:{int(time.time() / window)}"
    return get_cache(key) or 0
