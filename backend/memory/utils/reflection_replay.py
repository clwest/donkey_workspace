from __future__ import annotations
import logging
from typing import Optional, List
from django.utils import timezone

from assistants.models.reflection import AssistantReflectionLog
from memory.models import (
    MemoryEntry,
    SymbolicMemoryAnchor,
    ReflectionReplayLog,
)
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

from intel_core.utils.glossary_tagging import _match_anchor


logger = logging.getLogger(__name__)


def replay_reflection(obj: AssistantReflectionLog | MemoryEntry) -> ReflectionReplayLog | None:
    """Replay a reflection or memory entry using current glossary anchors."""
    if isinstance(obj, MemoryEntry):
        assistant = obj.assistant
        engine = AssistantReflectionEngine(assistant)
        prompt = engine.build_reflection_prompt([obj.summary or obj.event])
        summary = engine.generate_reflection(prompt)
        old_score = 0.0
        original_reflection = None
        original_text = obj.summary or obj.event or ""
        memory_entry = obj
    else:
        assistant = obj.assistant
        engine = AssistantReflectionEngine(assistant)
        prompt = obj.raw_prompt or obj.summary
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

    # update anchor usage
    if original_reflection and original_reflection.anchor:
        anchor = original_reflection.anchor
        anchor.last_used_in_reflection = timezone.now()
        anchor.save(update_fields=["last_used_in_reflection"])

    return replay_log

