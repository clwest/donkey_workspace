from __future__ import annotations

import re
from typing import List

from agents.models import SwarmMemoryEntry


METAPHOR_MAP = {
    "fear": "cracked mirror",
    "anxiety": "cracked mirror",
    "uncertain": "cracked mirror",
    "connection": "bridge of echoes",
    "reach": "bridge of echoes",
    "communicat": "bridge of echoes",
    "forge": "haunted forge",
    "craft": "haunted forge",
    "create": "haunted forge",
}


def generate_metaphor_tags(memory_entry: SwarmMemoryEntry) -> List[str]:
    """Return a list of metaphor tags derived from memory content."""

    text = f"{memory_entry.title} {memory_entry.content}".lower()
    tags: list[str] = []
    for keyword, metaphor in METAPHOR_MAP.items():
        if re.search(keyword, text):
            if metaphor not in tags:
                tags.append(metaphor)
    if not tags:
        tags.append("fog of memory")
    return tags[:3]
