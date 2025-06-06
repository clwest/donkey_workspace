from __future__ import annotations
import logging
from typing import Optional, List
from django.utils import timezone

from assistants.models.reflection import AssistantReflectionLog
from memory.models import MemoryEntry, SymbolicMemoryAnchor, ReflectionReplayLog
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from utils.similarity.prompt_similarity import score_reflection_diff

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
    )

    # update anchor usage
    if original_reflection and original_reflection.anchor:
        anchor = original_reflection.anchor
        anchor.last_used_in_reflection = timezone.now()
        anchor.save(update_fields=["last_used_in_reflection"])

    return replay_log

