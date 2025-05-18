import logging
from django.core.cache import cache

logger = logging.getLogger("django")


def get_cache(key):
    try:
        data = cache.get(key)
        logger.info(f"✅ Cache {'hit' if data else 'miss'} for key: {key}")
        return data
    except Exception as e:
        logger.error(f"❌ Error retrieving cache {key}: {e}")
        return None


def set_cache(key, data, timeout=3600):
    try:
        cache.set(key, data, timeout=timeout)
        logger.info(f"✅ Cache set for key: {key} with timeout {timeout}s")
        return True
    except Exception as e:
        logger.error(f"❌ Error setting cache {key}: {e}")
        return False


def delete_cache(key):
    try:
        cache.delete(key)
        logger.info(f"🗑 Cache deleted for key: {key}")
    except Exception as e:
        logger.error(f"❌ Error deleting cache {key}: {e}")


def clear_cache():
    try:
        cache.clear()
        logger.info("🧹 Full cache cleared")
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}")
