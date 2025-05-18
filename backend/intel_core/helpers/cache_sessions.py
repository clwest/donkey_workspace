from .cache_core import get_cache, set_cache, delete_cache


def get_session_data(session_id, key):
    return get_cache(f"session:{session_id}:{key}")


def store_session_data(session_id, key, data, ttl=1800):
    return set_cache(f"session:{session_id}:{key}", data, ttl)


def clear_session_data(session_id, key=None):
    if key:
        return delete_cache(f"session:{session_id}:{key}")
    return False
