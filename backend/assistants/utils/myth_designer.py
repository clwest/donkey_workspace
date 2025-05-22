from __future__ import annotations

from typing import List

from assistants.models.assistant import Assistant


class LoreEntry:
    """Simple lore entry placeholder for myth-based assistant generation."""

    def __init__(
        self,
        title: str,
        tone: str = "mystic",
        arcs: list[str] | None = None,
        epithets: list[str] | None = None,
        traits: list[str] | None = None,
        lineage: str | None = None,
    ):
        self.title = title
        self.tone = tone
        self.arcs = arcs or []
        self.epithets = epithets or []
        self.traits = traits or []
        self.lineage = lineage or "unknown"


def design_assistant_from_myth(lore_entry: LoreEntry) -> Assistant:
    """Create a new Assistant based on a lore entry."""

    name = lore_entry.title
    description = f"Myth-born from {lore_entry.lineage}"
    persona_summary = ", ".join(lore_entry.epithets)

    assistant = Assistant.objects.create(
        name=name,
        description=description,
        specialty="mythic guide",
        tone=lore_entry.tone,
        persona_summary=persona_summary,
        traits=lore_entry.traits,
    )
    return assistant
