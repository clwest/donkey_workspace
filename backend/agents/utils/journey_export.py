from __future__ import annotations

import json
import os
from typing import Any

from assistants.models.assistant import Assistant
from agents.models.lore import (
    SwarmMemoryEntry,
    SwarmCodex,
    EncodedRitualBlueprint,
    BeliefInheritanceTree,
    RitualResponseArchive,
)

EXPORT_DIR = "exports/journeys"


def generate_journey_export_package(
    assistant: Assistant,
    user_id: str,
    export_format: str = "json",
) -> str:
    """Compile a simple myth journey snapshot and return export file path."""

    os.makedirs(EXPORT_DIR, exist_ok=True)

    identity = {
        "assistant": assistant.name,
        "assistant_id": str(assistant.id),
        "user_id": user_id,
    }
    memories = list(
        SwarmMemoryEntry.objects.filter(created_by=assistant).values("id", "title")
    )
    codices = list(SwarmCodex.objects.filter(created_by=assistant).values("id", "title"))
    rituals = list(
        EncodedRitualBlueprint.objects.all().values("id", "name")[:5]
    )
    belief_trees = list(
        BeliefInheritanceTree.objects.filter(user_id=user_id, assistant=assistant)
        .values("id", "symbolic_summary")
    )
    archives = list(
        RitualResponseArchive.objects.filter(user_id=user_id, assistant=assistant)
        .values("id", "output_summary")
    )

    package: dict[str, Any] = {
        "identity": identity,
        "memory_map": memories,
        "codex_anchors": codices,
        "ritual_contracts": rituals,
        "belief_inheritance": belief_trees,
        "ritual_archives": archives,
    }

    filename = f"journey_{assistant.slug}_{user_id}.{export_format}"
    path = os.path.join(EXPORT_DIR, filename)

    if export_format == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
    elif export_format == "md":
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Myth Journey for {assistant.name}\n\n")
            f.write(json.dumps(package, indent=2))
    else:
        # Placeholder for other formats
        with open(path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2, ensure_ascii=False)

    return path
