from collections import Counter
import re
from typing import List, Tuple

from django.utils.text import slugify

from assistants.models import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import AssistantReflectionLog
from memory.models import MemoryEntry, SymbolicMemoryAnchor


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9-]{3,}", text.lower())


def infer_symbolic_anchors_from_memory(
    assistant: Assistant,
) -> List[Tuple[SymbolicMemoryAnchor, int]]:
    """Infer likely glossary anchors from an assistant's memory."""
    texts: List[str] = []

    reflections = AssistantReflectionLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )[:100]
    texts.extend([r.summary or r.title for r in reflections if r.summary or r.title])

    thoughts = AssistantThoughtLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )[:100]
    texts.extend([t.thought for t in thoughts if t.thought])

    memories = MemoryEntry.objects.filter(assistant=assistant).order_by("-created_at")[
        :200
    ]
    for mem in memories:
        if mem.summary:
            texts.append(mem.summary)
        texts.append(mem.event)
        texts.extend(list(mem.tags.values_list("slug", flat=True)))

    counter: Counter[str] = Counter()
    for txt in texts:
        counter.update(_tokenize(txt))

    anchors: List[Tuple[SymbolicMemoryAnchor, int]] = []
    if not counter:
        return anchors

    for token, count in counter.items():
        if count < 3:
            continue
        slug = slugify(token)
        anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
            slug=slug, defaults={"label": token.title()}
        )
        if not anchor.reinforced_by.filter(id=assistant.id).exists():
            anchor.reinforced_by.add(assistant)
        anchors.append((anchor, count))

    if anchors:
        max_score = max(c for _, c in anchors)
        profile = assistant.anchor_weight_profile or {}
        for anchor, cnt in anchors:
            weight = round(cnt / max_score, 2)
            profile[anchor.slug] = weight
        assistant.anchor_weight_profile = profile
        assistant.save(update_fields=["anchor_weight_profile"])

    return anchors
