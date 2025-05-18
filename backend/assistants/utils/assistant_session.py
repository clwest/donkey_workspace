import json
from datetime import datetime
from django.utils import timezone
from assistants.models import Assistant, AssistantThoughtLog

# ⬇️ Pull redis config + helpers from shared helper
from assistants.helpers.redis_helpers import r, SESSION_EXPIRY
import logging

logger = logging.getLogger("assistants")


def save_message_to_session(session_id: str, role: str, content: str):
    print(f"[🧠 SAVE SESSION] {session_id} ({role}): {content[:60]}...")
    payload = json.dumps(
        {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
    )
    r.rpush(f"chat:{session_id}", payload)
    r.expire(f"chat:{session_id}", SESSION_EXPIRY)
    print(
        f"[REDIS TEST] DB={r.connection_pool.connection_kwargs.get('db')} Ping={r.ping()}"
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
            logger.warning(f"Failed to archive message: {e}", exc_info=True)
            continue

    # Commented out for inspection
    # r.delete(key)

    return saved
