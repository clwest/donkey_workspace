import json
import logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings
import redis

from assistants.models.assistant import Assistant
from assistants.models.thoughts import AssistantThoughtLog

REDIS_URL = getattr(settings, "REDIS_URL", "redis://127.0.0.1:6379/1")
r = redis.Redis.from_url(REDIS_URL)

SESSION_EXPIRY = getattr(settings, "TOPIC_MEMORY_EXPIRY", 3600)
THOUGHT_CACHE_PREFIX = "assistant:thoughts:"
THOUGHT_TTL_SECONDS = 60 * 5  # 5 minutes

logger = logging.getLogger(__name__)


def save_message_to_session(session_id: str, role: str, content: str) -> None:
    payload = json.dumps(
        {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
    )
    r.rpush(f"chat:{session_id}", payload)
    r.expire(f"chat:{session_id}", SESSION_EXPIRY)
    logger.debug(
        "Saved message to session",
        extra={"session_id": session_id, "role": role},
    )


def load_session_messages(session_id: str) -> list:
    raw = r.lrange(f"chat:{session_id}", 0, -1)
    messages = [json.loads(msg) for msg in raw]
    logger.debug(
        "Loaded messages from session",
        extra={"session_id": session_id, "count": len(messages)},
    )
    return messages


def flush_chat_session(session_id: str) -> None:
    r.delete(f"chat:{session_id}")
    logger.info("Flushed chat session", extra={"session_id": session_id})


def flush_session_to_db(session_id: str, assistant: Assistant) -> int:
    key = f"chat:{session_id}"
    messages = r.lrange(key, 0, -1)
    if not messages:
        logger.info(
            "No messages to flush",
            extra={"session_id": session_id, "assistant": assistant.slug},
        )
        return 0

    saved = 0
    for raw in messages:
        try:
            entry = json.loads(raw)
            AssistantThoughtLog.objects.create(
                assistant=assistant,
                thought=entry.get("content", ""),
                thought_trace="• Archived from chat session\n• Role: "
                + entry.get("role", "unknown"),
                created_at=datetime.fromisoformat(
                    entry.get("timestamp", timezone.now().isoformat())
                ),
                role=entry.get("role", "assistant"),
            )
            saved += 1
        except Exception as e:  # pragma: no cover - safeguard
            logger.warning(
                "Failed to archive message",
                extra={
                    "session_id": session_id,
                    "assistant": assistant.slug,
                    "error": str(e),
                },
                exc_info=True,
            )
            continue
    logger.info(
        "Flushed session to DB",
        extra={"session_id": session_id, "assistant": assistant.slug, "count": saved},
    )
    return saved


def get_cached_thoughts(assistant_slug: str) -> list | None:
    key = f"{THOUGHT_CACHE_PREFIX}{assistant_slug}"
    raw = r.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_cached_thoughts(assistant_slug: str, thoughts: list) -> None:
    key = f"{THOUGHT_CACHE_PREFIX}{assistant_slug}"
    try:
        serialized = json.dumps(thoughts)
        r.set(key, serialized, ex=THOUGHT_TTL_SECONDS)
    except Exception:  # pragma: no cover - ignore caching issues
        pass


def get_cached_reflection(slug: str) -> dict | None:
    key = f"reflection:{slug}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_reflection(slug: str, summary: str, ttl: int = 3600):
    key = f"reflection:{slug}"
    r.setex(key, ttl, json.dumps(summary))
