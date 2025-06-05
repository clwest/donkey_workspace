import json
import logging
from mcp_core.models import Tag
from memory.models import MemoryEntry
from assistants.tasks import embed_and_tag_memory, run_assistant_reflection
from assistants.tasks import detect_emotional_resonance
from embeddings.helpers.helpers_io import save_embedding


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
    thread=None,
    tool_response=None,
    anchor_slug=None,
    fallback_reason=None,
):
    transcript = "\n".join(
        [
            f"{m['role'].capitalize()}: {m['content'].strip()}"
            for m in messages
            if m["role"] in ("user", "assistant")
        ]
        + [f"Assistant: {reply}"]
    )

    if not thread and chat_session:
        thread = chat_session.thread or chat_session.narrative_thread
    if not thread and project:
        thread = project.thread or project.narrative_thread
    if not narrative_thread:
        narrative_thread = thread

    identity = assistant.get_identity_prompt() if assistant else ""
    event_text = f"Conversation with assistant {assistant_name}"
    if identity:
        event_text += f" | {identity}"
    memory_kwargs = dict(
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
        thread=thread,
        tool_response=tool_response,
    )

    if anchor_slug:
        from memory.models import SymbolicMemoryAnchor

        anchor_obj = SymbolicMemoryAnchor.objects.filter(slug=anchor_slug).first()
        if anchor_obj:
            memory_kwargs["anchor"] = anchor_obj

    if fallback_reason:
        memory_kwargs["triggered_by"] = f"RAG Fallback: {fallback_reason}"

    memory = MemoryEntry.objects.create(**memory_kwargs)

    if anchor_slug:
        tag, _ = Tag.objects.get_or_create(slug=anchor_slug, defaults={"name": anchor_slug})
        memory.tags.add(tag)
        gloss_tag, _ = Tag.objects.get_or_create(slug="glossary_insight", defaults={"name": "glossary_insight"})
        memory.tags.add(gloss_tag)

    if fallback_reason:
        fb_tag, _ = Tag.objects.get_or_create(slug="rag_fallback", defaults={"name": "rag_fallback"})
        memory.tags.add(fb_tag)

    embed_and_tag_memory.delay(memory.id)
    run_assistant_reflection.delay(memory.id)
    detect_emotional_resonance.delay(str(memory.id))
    from .team_memory import propagate_memory_to_team_chain

    propagate_memory_to_team_chain(memory)
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
