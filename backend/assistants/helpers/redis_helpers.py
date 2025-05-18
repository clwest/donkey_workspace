import redis
import json
from django.conf import settings
from django.utils import timezone

# Central Redis connection
REDIS_URL = getattr(settings, "REDIS_URL", "redis://127.0.0.1:6379/1")
r = redis.Redis.from_url(REDIS_URL)

# Constants
SESSION_EXPIRY = getattr(settings, "TOPIC_MEMORY_EXPIRY", 3600)
THOUGHT_CACHE_PREFIX = "assistant:thoughts:"
THOUGHT_TTL_SECONDS = 60 * 5  # 5 minutes


# Session storage
def save_message_to_session(session_id: str, role: str, content: str):
    payload = json.dumps(
        {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
    )
    r.rpush(f"chat:{session_id}", payload)
    r.expire(f"chat:{session_id}", SESSION_EXPIRY)


def load_session_messages(session_id: str) -> list:
    raw = r.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(msg) for msg in raw]


# Thought caching
def get_cached_thoughts(assistant_slug: str) -> list[dict] | None:
    key = f"{THOUGHT_CACHE_PREFIX}{assistant_slug}"
    raw = r.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_cached_thoughts(assistant_slug: str, thoughts: list[dict]) -> None:
    key = f"{THOUGHT_CACHE_PREFIX}{assistant_slug}"
    try:
        serialized = json.dumps(thoughts)
        r.set(key, serialized, ex=THOUGHT_TTL_SECONDS)
    except Exception:
        pass


# Reflection caching
def get_cached_reflection(slug: str) -> dict | None:
    key = f"reflection:{slug}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_reflection(slug: str, summary: str, ttl: int = 3600):
    key = f"reflection:{slug}"
    r.setex(key, ttl, json.dumps(summary))
