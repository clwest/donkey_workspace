from typing import List, Dict
from memory.models import MemoryEntry


def build_project_plan_from_memories(memories: List[MemoryEntry], planning_style: str = "bullet", title: str | None = None) -> Dict:
    """Generate a basic project plan from memory entries.

    This is a placeholder planning engine used for tests. It simply
    derives objectives from memory summaries and creates one task per
    objective.
    """
    if not memories:
        raise ValueError("memories list cannot be empty")

    title = title or f"Project from {len(memories)} memories"

    objectives = []
    for mem in memories[:5]:
        text = mem.summary or mem.event[:60]
        objectives.append(text.strip())

    tasks = [
        {"title": f"Task for {obj}"} for obj in objectives
    ]

    milestones = [
        {"title": f"Milestone {i+1}", "description": obj}
        for i, obj in enumerate(objectives)
    ]

    return {
        "title": title,
        "objectives": objectives,
        "tasks": tasks,
        "milestones": milestones,
    }
