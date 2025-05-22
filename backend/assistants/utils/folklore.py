from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import random

from agents.models.lore import SwarmMemoryEntry
from assistants.models.core import AssistantMythLayer


@dataclass
class LoreEntry:
    title: str
    text: str
    season: Optional[str] = None


def generate_swarm_folklore(season: str | None = None) -> LoreEntry:
    """Compose emergent lore from swarm memory and myth layers."""

    memories = SwarmMemoryEntry.objects.all()
    if season:
        memories = memories.filter(season=season)
    memory_snippets = list(memories.order_by("-created_at").values_list("content", flat=True)[:5])

    myths = AssistantMythLayer.objects.filter(archived=False).order_by("-created_at")
    myth_snippets = list(myths.values_list("summary", flat=True)[:5])

    all_lines = memory_snippets + myth_snippets
    random.shuffle(all_lines)
    text = "\n".join(f"• {line}" for line in all_lines)
    title = f"Swarm Lore - {season}" if season else "Swarm Lore"
    return LoreEntry(title=title, text=text, season=season)
