from __future__ import annotations

import re
from typing import List

from django.utils.text import slugify

from memory.models import (
    MemoryFeedback,
    SymbolicMemoryAnchor,
    GlossaryChangeEvent,
    AnchorConvergenceLog,
)

__all__ = ["apply_feedback_suggestion", "extract_anchor_slugs"]


def extract_anchor_slugs(text: str) -> List[str]:
    """Return list of existing anchor slugs mentioned in the text."""
    if not text:
        return []

    lower = text.lower()
    slugs = set(re.findall(r"\[([^\]]+)\]", lower))

    known = list(SymbolicMemoryAnchor.objects.values_list("slug", "label"))
    for slug, label in known:
        slug_spaces = slug.replace("-", " ")
        if slug in lower or slug_spaces in lower or label.lower() in lower:
            slugs.add(slug)

    return list(slugs)


def apply_feedback_suggestion(feedback: MemoryFeedback, *, increment: float = 0.1) -> None:
    """Apply glossary feedback effects based on suggestion text."""
    slugs = extract_anchor_slugs(feedback.suggestion)
    assistant = feedback.memory.assistant if feedback.memory else None

    if not slugs:
        # no matching anchors, record suggestion as GlossaryChangeEvent
        GlossaryChangeEvent.objects.create(
            term=feedback.suggestion.strip(),
            boost=0.0,
            created_by=feedback.submitted_by,
        )
        return

    for slug in slugs:
        anchor, created = SymbolicMemoryAnchor.objects.get_or_create(slug=slug, defaults={"label": slug})
        if not created:
            anchor.score_weight = round(anchor.score_weight + increment, 2)
            anchor.save(update_fields=["score_weight"])

        AnchorConvergenceLog.objects.create(
            anchor=anchor,
            assistant=assistant,
            memory=feedback.memory,
            guidance_used=False,
            retried=False,
            final_score=anchor.score_weight,
        )
