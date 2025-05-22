from __future__ import annotations

from typing import Dict, List

from agents.models.lore import SwarmCodex, SwarmMemoryEntry, SymbolicLawEntry


def myth_api_lookup(query: str) -> Dict[str, List[dict]]:
    """Very simple symbolic search across codices, laws and memories."""
    q = query or ""
    codices = list(
        SwarmCodex.objects.filter(title__icontains=q).values("id", "title")
    )
    memories = list(
        SwarmMemoryEntry.objects.filter(content__icontains=q).values("id", "title")
    )
    laws = list(
        SymbolicLawEntry.objects.filter(description__icontains=q).values("id", "description")
    )
    return {"codices": codices, "memories": memories, "laws": laws}
