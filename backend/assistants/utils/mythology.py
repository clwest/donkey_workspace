"""Myth network utilities for assistants."""

from __future__ import annotations

import re
from django.utils.text import slugify

from assistants.models.assistant import Assistant
from agents.models.lore import LoreEntry, SwarmMemoryEntry
from mcp_core.models import Tag


def _tokenize(text: str) -> set[str]:
    """Return a set of lowercase word tokens from text."""
    return set(re.findall(r"\b\w+\b", (text or "").lower()))


def score_symbolic_convergence(assistant: Assistant, lore_entry: LoreEntry) -> float:
    """Simple heuristic comparing assistant traits to lore summary."""

    tokens = set()
    tokens.update(_tokenize(assistant.persona_summary or ""))
    tokens.update(_tokenize(assistant.personality_description or ""))

    traits = assistant.traits or []
    if isinstance(traits, dict):
        tokens.update(_tokenize(" ".join(k for k, v in traits.items() if v)))
    elif isinstance(traits, list):
        tokens.update(_tokenize(" ".join(traits)))

    lore_tokens = _tokenize(lore_entry.title) | _tokenize(lore_entry.summary or "")
    if not lore_tokens:
        return 0.0

    overlap = tokens.intersection(lore_tokens)
    score = len(overlap) / len(lore_tokens)
    return round(max(0.0, min(score, 1.0)), 2)


def trigger_metamorphosis(assistant: Assistant) -> dict:
    """Create a transformation memory entry and tweak assistant attributes."""

    new_title = f"{assistant.name} Awakened"
    assistant.name = new_title
    assistant.tone = (assistant.tone or "").split("|")[0].strip() + " | evolved"
    assistant.save(update_fields=["name", "tone"])

    entry = SwarmMemoryEntry.objects.create(
        title=f"Metamorphosis: {assistant.name}",
        content=f"Assistant {assistant.slug} underwent metamorphosis.",
        origin="metamorphosis",
    )

    for label in ["metamorphosis", "threshold-crossing", "symbolic-sync"]:
        tag, _ = Tag.objects.get_or_create(name=label, defaults={"slug": slugify(label)})
        entry.tags.add(tag)

    return {"new_title": assistant.name, "memory_entry": entry.id}
