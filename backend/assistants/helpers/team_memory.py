from typing import Optional
from assistants.models import Assistant, AssistantMemoryChain, AssistantReflectionLog
from memory.models import MemoryEntry
from project.models import Project, ProjectParticipant


def assign_project_role(assistant: Assistant, project: Project, role: str) -> None:
    """Assign a role to an assistant's user within the project team."""
    if assistant.created_by:
        ProjectParticipant.objects.update_or_create(
            user=assistant.created_by,
            project=project,
            defaults={"role": role},
        )
    project.team.add(assistant)
    project.save()


def get_visible_memories(project: Project, assistant: Optional[Assistant]):
    chain = project.team_chain
    if not chain:
        return MemoryEntry.objects.none()
    memories = chain.memories.all()
    if (
        chain.visibility_scope == "assigned_only"
        and assistant not in project.team.all()
    ):
        return MemoryEntry.objects.none()
    if chain.visibility_scope == "owner_only" and assistant != project.assistant:
        return MemoryEntry.objects.none()
    if chain.shared_tags:
        memories = memories.filter(tags__slug__in=chain.shared_tags).distinct()
    return memories.order_by("-created_at")


def propagate_memory_to_team_chain(memory: MemoryEntry) -> None:
    project = memory.related_project
    if not project or not project.team_chain:
        return
    chain = project.team_chain
    if chain.shared_tags:
        if not memory.tags.filter(slug__in=chain.shared_tags).exists():
            return
    chain.memories.add(memory)
