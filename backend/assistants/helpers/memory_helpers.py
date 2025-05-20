import json
import logging
from openai import OpenAI
from django.utils.text import slugify
from mcp_core.models import Tag
from memory.models import MemoryEntry
from assistants.tasks import embed_and_tag_memory, run_assistant_reflection
from assistants.tasks import detect_emotional_resonance
from embeddings.helpers.helpers_io import save_embedding


client = OpenAI()
logger = logging.getLogger(__name__)


import re


def create_memory_from_chat(
    assistant_name,
    session_id,
    messages,
    reply,
    *,
    chat_session=None,
    assistant=None,
    project=None,
    importance=5,
    narrative_thread=None,
    tool_response=None,
):
    transcript = "\n".join(
        [
            f"{m['role'].capitalize()}: {m['content'].strip()}"
            for m in messages
            if m["role"] in ("user", "assistant")
        ]
        + [f"Assistant: {reply}"]
    )

    if not narrative_thread and chat_session:
        narrative_thread = chat_session.thread or chat_session.narrative_thread
    if not narrative_thread and project:
        narrative_thread = project.thread or project.narrative_thread

    identity = assistant.get_identity_prompt() if assistant else ""
    event_text = f"Conversation with assistant {assistant_name}"
    if identity:
        event_text += f" | {identity}"
    memory = MemoryEntry.objects.create(
        event=event_text,
        emotion="neutral",
        importance=importance,
        is_conversation=True,
        session_id=session_id,
        full_transcript=transcript,
        chat_session=chat_session,
        assistant=assistant,
        related_project=project,
        narrative_thread=narrative_thread,
        tool_response=tool_response,
    )

    embed_and_tag_memory.delay(memory.id)
    run_assistant_reflection.delay(memory.id)
    detect_emotional_resonance.delay(str(memory.id))
    return memory


def get_relevant_memories_for_task(
    assistant,
    project=None,
    task_type: str | None = None,
    context=None,
    limit: int = 10,
):
    """Return prioritized memories for a given task."""
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count

    qs = MemoryEntry.objects.filter(assistant=assistant)
    if context:
        qs = qs.filter(context=context)
    elif project:
        qs = qs.filter(related_project=project)

    if task_type:
        qs = qs.filter(context_tags__contains=[task_type])

    # default to last 30 days
    qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=30))

    qs = qs.annotate(feedback_count=Count("feedback"))
    qs = qs.order_by(
        "-relevance_score",
        "-importance",
        "-feedback_count",
        "-created_at",
    )
    return list(qs[:limit])
