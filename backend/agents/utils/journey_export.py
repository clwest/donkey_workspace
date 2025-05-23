
import json
import os
from typing import List

from agents.models.lore import (
    BeliefInheritanceTree,
    RitualResponseArchive,
    SwarmMemoryEntry,
)


def create_myth_journey_package(
    user_id: str,
    assistant,
    export_dir: str,
    *,
    memories: List[SwarmMemoryEntry] | None = None,
    format_list: List[str] | None = None,
):
    """Create a portable package of a user's myth journey."""

    os.makedirs(export_dir, exist_ok=True)
    format_list = format_list or ["json", "md"]

    belief_trees = BeliefInheritanceTree.objects.filter(user_id=user_id, assistant=assistant)
    rituals = RitualResponseArchive.objects.filter(user_id=user_id, assistant=assistant)

    data = {
        "user": user_id,
        "assistant": str(assistant),
        "belief_trees": [
            {
                "id": str(tree.id),
                "summary": tree.symbolic_summary,
                "created_at": tree.created_at.isoformat(),
            }
            for tree in belief_trees
        ],
        "ritual_archives": [
            {
                "id": str(r.id),
                "summary": r.output_summary,
                "created_at": r.created_at.isoformat(),
            }
            for r in rituals
        ],
        "memory_ids": [m.id for m in memories] if memories else [],
    }

    if "json" in format_list:
        with open(os.path.join(export_dir, "journey.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    if "md" in format_list:
        lines = [f"# Myth Journey for {user_id}", ""]
        lines.append(f"Assistant: {assistant}\n")
        lines.append("## Belief Trees")
        for tree in belief_trees:
            lines.append(f"- {tree.symbolic_summary}")
        lines.append("\n## Ritual Archives")
        for r in rituals:
            lines.append(f"- {r.output_summary}")
        with open(os.path.join(export_dir, "journey.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    return os.path.join(export_dir, "journey.json") if "json" in format_list else None

