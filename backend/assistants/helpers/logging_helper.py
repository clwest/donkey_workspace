from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.project import AssistantProject
from project.models import Project
from .mood import detect_mood, update_mood_stability
from memory.models import MemoryEntry
from mcp_core.models import Tag
from django.utils.text import slugify


def log_assistant_thought(
    assistant,
    thought: str,
    trace: str = "",
    linked_memory=None,
    linked_memories=None,
    linked_reflection=None,
    linked_event=None,
    project=None,
    thought_type: str = "generated",
    bookmark_label: str | None = None,
):
    """
    Save a thought from or about the assistant to the AssistantThoughtLog.
    """
    mood = detect_mood(thought)
    core_project = project
    if isinstance(project, AssistantProject):
        core_project = (
            project.linked_projects.first()
            or Project.objects.filter(assistant_project=project).first()
        )
    log = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=thought,
        thought_trace=trace or "",
        linked_memory=linked_memory,
        linked_reflection=linked_reflection,
        linked_event=linked_event,
        project=core_project,
        thought_type=thought_type,
        mood=mood,
        mood_snapshot={"mood": mood, "stability": assistant.mood_stability_index},
    )
    if linked_memories:
        log.linked_memories.set(linked_memories)
    update_mood_stability(assistant, mood)
    if bookmark_label and linked_memory:
        linked_memory.is_bookmarked = True
        linked_memory.bookmark_label = bookmark_label
        linked_memory.save()
    return log


def log_assistant_birth_event(assistant, user):
    """Record an origin memory when a new assistant is created or personalized."""
    spawned_by_label = getattr(assistant, "spawned_by_label", None) or (
        assistant.spawned_by.name if assistant.spawned_by else "scratch"
    )
    content = f"{assistant.name} was created from {spawned_by_label} and personalized by {user.username}."
    memory = MemoryEntry.objects.create(
        assistant=assistant,
        context=assistant.memory_context,
        event=content,
        title="Assistant Created",
        type="origin",
        source_role="system",
        source_user=user,
    )
    for label in ["birth", "demo", "personalization"]:
        tag, _ = Tag.objects.get_or_create(
            slug=slugify(label), defaults={"name": label}
        )
        memory.tags.add(tag)
    return memory
