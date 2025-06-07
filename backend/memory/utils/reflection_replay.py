from __future__ import annotations
import logging
from typing import Optional, List
from django.utils import timezone

from assistants.models.reflection import AssistantReflectionLog
from memory.models import (
    MemoryEntry,
    SymbolicMemoryAnchor,
    ReflectionReplayLog,
    RAGPlaybackLog,
)
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

from intel_core.utils.glossary_tagging import _match_anchor
from assistants.utils.chunk_retriever import get_relevant_chunks
from utils.rag_playback import record_rag_playback
from memory.services.acquisition import update_anchor_acquisition


logger = logging.getLogger(__name__)


def replay_reflection(obj: AssistantReflectionLog | MemoryEntry) -> ReflectionReplayLog | None:
    """Replay a reflection or memory entry using current glossary anchors."""
    if isinstance(obj, MemoryEntry):
        assistant = obj.assistant
        engine = AssistantReflectionEngine(assistant)
        prompt = engine.build_reflection_prompt([obj.summary or obj.event])
        chunk_info, *_ = get_relevant_chunks(
            str(assistant.id),
            obj.summary or obj.event or "",
            memory_context_id=str(assistant.memory_context_id)
            if assistant.memory_context_id
            else None,
            debug=True,
        )
        playback = record_rag_playback(
            obj.summary or obj.event or "",
            assistant,
            assistant.memory_context,
            chunk_info,
            query_term=obj.summary or obj.event or "",
            playback_type=RAGPlaybackLog.PlaybackType.REPLAY,
        )
        summary = engine.generate_reflection(prompt)
        old_score = 0.0
        original_reflection = None
        original_text = obj.summary or obj.event or ""
        memory_entry = obj
    else:
        assistant = obj.assistant
        engine = AssistantReflectionEngine(assistant)
        prompt = obj.raw_prompt or obj.summary
        chunk_info, *_ = get_relevant_chunks(
            str(assistant.id),
            obj.summary or "",
            memory_context_id=str(assistant.memory_context_id)
            if assistant.memory_context_id
            else None,
            debug=True,
        )
        playback = record_rag_playback(
            obj.summary or "",
            assistant,
            assistant.memory_context,
            chunk_info,
            query_term=obj.summary or "",
            playback_type=RAGPlaybackLog.PlaybackType.REPLAY,
        )
        summary = engine.generate_reflection(prompt)
        old_score = 0.0
        original_reflection = obj
        original_text = obj.summary or ""
        memory_entry = obj.linked_memory

    new_score = score_reflection_diff(original_text, summary)
    replay_log = ReflectionReplayLog.objects.create(
        original_reflection=original_reflection,
        assistant=assistant,
        memory_entry=memory_entry,
        old_score=old_score,
        new_score=new_score,
        reflection_score=0.0,
        changed_anchors=[],
        replayed_summary=summary,
        rag_playback=playback,
    )

    # detect glossary anchors in the reflection text
    if isinstance(obj, MemoryEntry):
        text = " ".join(filter(None, [summary, obj.event, obj.summary]))
    else:
        text = " ".join(filter(None, [summary, obj.summary, obj.llm_summary, obj.raw_prompt]))
    matched = []
    for anchor in SymbolicMemoryAnchor.objects.all():
        found, _ = _match_anchor(anchor, text)
        if found:
            matched.append(anchor)

    if original_reflection and matched:
        original_reflection.related_anchors.set(matched)
        replay_log.changed_anchors = [a.slug for a in matched]
        replay_log.save(update_fields=["changed_anchors"])
        for a in matched:
            update_anchor_acquisition(a, "acquired")

    # update anchor usage
    if original_reflection and original_reflection.anchor:
        anchor = original_reflection.anchor
        anchor.last_used_in_reflection = timezone.now()
        anchor.save(update_fields=["last_used_in_reflection"])
        update_anchor_acquisition(anchor, "acquired")

    return replay_log


def queue_drifted_reflections(assistant_slug: str | None = None) -> int:
    """Queue reflections with high drift or pending anchors for replay."""
    from django.db.models import Count, Q

    qs = AssistantReflectionLog.objects.all()
    if assistant_slug:
        qs = qs.filter(assistant__slug=assistant_slug)

    qs = qs.annotate(
        pending_count=Count(
            "related_anchors",
            filter=Q(related_anchors__mutation_status="pending"),
        )
    ).filter(
        Q(replays__reflection_score__gt=0.6) | Q(pending_count__gt=0)
    ).distinct()

    queued = 0
    for ref in qs:
        try:
            replay = replay_reflection(ref)
            if replay:
                replay.is_priority = True
                replay.save(update_fields=["is_priority"])
                queued += 1
        except Exception as exc:  # pragma: no cover - safeguard
            logger.exception("Queue drifted replay failed: %s", exc)
    return queued


