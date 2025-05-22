import json
import logging
from datetime import datetime
from django.utils import timezone
from assistants.models import Assistant, AssistantThoughtLog
from assistants.helpers.redis_helpers import r, SESSION_EXPIRY

logger = logging.getLogger(__name__)


def save_message_to_session(session_id: str, role: str, content: str) -> None:
    """Persist a chat message to Redis."""
    payload = json.dumps(
        {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
    )
    r.rpush(f"chat:{session_id}", payload)
    r.expire(f"chat:{session_id}", SESSION_EXPIRY)
    logger.debug(
        "Saved message to session", extra={"session_id": session_id, "role": role}
    )


def load_session_messages(session_id: str) -> list:
    """Retrieve all messages for a given session from Redis."""
    raw = r.lrange(f"chat:{session_id}", 0, -1)
    messages = [json.loads(msg) for msg in raw]
    logger.debug(
        "Loaded messages from session",
        extra={"session_id": session_id, "count": len(messages)},
    )
    return messages


def flush_chat_session(session_id: str) -> None:
    """Delete all messages for the given session from Redis."""
    r.delete(f"chat:{session_id}")
    logger.info("Flushed chat session", extra={"session_id": session_id})


def flush_session_to_db(session_id: str, assistant: Assistant) -> int:
    """Archive messages from Redis into AssistantThoughtLog records."""
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
        except Exception as e:
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
