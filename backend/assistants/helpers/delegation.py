import logging

from assistants.utils.delegation import spawn_delegated_assistant as _spawn
from memory.models import MemoryEntry


logger = logging.getLogger(__name__)


def spawn_delegated_assistant(session, *, reason="token_limit", summary=None):
    """Spawn a delegate for the given chat ``session``.

    This is a thin wrapper around :func:`assistants.utils.delegation.spawn_delegated_assistant`
    used by the thought engine when a conversation exceeds the token limit. The
    latest memory entry for the session is passed through so the resulting
    ``DelegationEvent`` links back to the triggering context.
    """

    logger.info("Spawning delegated assistant for session %s", session.session_id)

    memory = (
        MemoryEntry.objects.filter(chat_session=session)
        .order_by("-created_at")
        .first()
    )

    return _spawn(
        session,
        memory_entry=memory,
        reason=reason,
        summary=summary,
    )
