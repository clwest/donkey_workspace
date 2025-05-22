import json
from datetime import datetime
from django.utils import timezone
from assistants.models import Assistant, AssistantThoughtLog

# ⬇️ Pull redis config + helpers from shared helper
from assistants.helpers.redis_helpers import r, SESSION_EXPIRY
import logging

logger = logging.getLogger(__name__)


def save_message_to_session(
    session_id: str, role: str, content: str, assistant_slug: str | None = None
):
    logger.debug(
        "[🧠 SAVE SESSION] %s (%s) slug=%s preview=%s",
        session_id,
        role,
        assistant_slug or "unknown",
        content[:60],
    )
    payload = json.dumps(
        {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
    )
    r.rpush(f"chat:{session_id}", payload)
    r.expire(f"chat:{session_id}", SESSION_EXPIRY)
    logger.debug(
        "[REDIS TEST] session=%s slug=%s DB=%s Ping=%s",
        session_id,
        assistant_slug or "unknown",
        r.connection_pool.connection_kwargs.get("db"),
        r.ping(),
    )


def load_session_messages(session_id: str) -> list:
    raw = r.lrange(f"chat:{session_id}", 0, -1)
    return [json.loads(msg) for msg in raw]


def flush_chat_session(session_id: str):
    r.delete(f"chat:{session_id}")


def flush_session_to_db(session_id: str, assistant: Assistant):
    """
    Archive all messages in the Redis session into AssistantThoughtLog records.
    (TEMP VERSION: Leaves Redis key intact for debugging)
    """
    key = f"chat:{session_id}"
    messages = r.lrange(key, 0, -1)
    logger.debug(
        "Flushing session %s for assistant %s with %d messages",
        session_id,
        assistant.slug,
        len(messages),
    )

    if not messages:
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
                    entry.get("timestamp", datetime.utcnow().isoformat())
                ),
                role=entry.get("role", "assistant"),
            )
            saved += 1
        except Exception as e:
            logger.warning(
                "Failed to archive message for session %s slug=%s: %s",
                session_id,
                assistant.slug,
                e,
                exc_info=True,
            )
            continue

    # Commented out for inspection
    # r.delete(key)

    return saved
