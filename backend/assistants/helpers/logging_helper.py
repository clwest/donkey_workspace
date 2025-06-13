from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.project import AssistantProject
from assistants.models.reflection import AssistantReflectionLog
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from django.conf import settings
from django.utils import timezone
import requests
from project.models import Project
from .mood import detect_mood, update_mood_stability
from memory.models import MemoryEntry
from mcp_core.models import Tag
from assistants.models.trail import TrailMarkerLog
from django.utils.text import slugify
import logging


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


def log_trail_marker(assistant, marker_type: str, memory=None, notes=None):
    """Record a lifecycle milestone for an assistant."""

    return TrailMarkerLog.objects.create(
        assistant=assistant,
        marker_type=marker_type,
        related_memory=memory,
        notes=notes or "",
    )


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
    log_trail_marker(assistant, "birth", memory)
    return memory


def reflect_on_birth(assistant):
    """Generate an initial reflection when an assistant is first created."""

    origin = (
        MemoryEntry.objects.filter(assistant=assistant, type="origin")
        .order_by("created_at")
        .first()
    )
    spawned_by_label = getattr(assistant, "spawned_by_label", None) or (
        assistant.spawned_by.name if assistant.spawned_by else "scratch"
    )
    prompt = (
        f"You are {assistant.name}. You were just created from {spawned_by_label}.\n"
        "Reflect on your purpose, your expected role, and any immediate goals you want to achieve for your user.\n"
        "Write 3–5 bullet points as internal thoughts."
    )

    engine = AssistantReflectionEngine(assistant)
    assistant.last_reflection_attempted_at = timezone.now()

    if not getattr(settings, "ENABLE_BIRTH_REFLECTIONS", True):
        logging.getLogger(__name__).info("Birth reflections disabled; skipping")
        assistant.last_reflection_successful = False
        assistant.reflection_error = "disabled"
        assistant.can_retry_birth_reflection = False
        assistant.save(
            update_fields=[
                "last_reflection_attempted_at",
                "last_reflection_successful",
                "reflection_error",
                "can_retry_birth_reflection",
            ]
        )
        return None

    if not getattr(settings, "ENABLE_LOCAL_CHAT_REFLECTIONS", True):
        logging.getLogger(__name__).info("Local chat reflections disabled; skipping")
        assistant.last_reflection_successful = False
        assistant.reflection_error = "disabled"
        assistant.can_retry_birth_reflection = False
        assistant.save(
            update_fields=[
                "last_reflection_attempted_at",
                "last_reflection_successful",
                "reflection_error",
                "can_retry_birth_reflection",
            ]
        )
        return None

    try:
        text = engine.generate_reflection(prompt)
        assistant.last_reflection_successful = True
        assistant.reflection_error = ""
        assistant.can_retry_birth_reflection = False
    except requests.exceptions.ConnectionError as e:
        logging.getLogger(__name__).warning(
            "[WARN] Assistant boot reflection skipped: LLM at localhost:11434 unreachable"
        )
        assistant.last_reflection_successful = False
        assistant.reflection_error = str(e)
        assistant.can_retry_birth_reflection = True
        assistant.save(
            update_fields=[
                "last_reflection_attempted_at",
                "last_reflection_successful",
                "reflection_error",
                "can_retry_birth_reflection",
            ]
        )
        return None
    except Exception as e:
        logging.getLogger(__name__).error("Failed to generate birth reflection: %s", e)
        assistant.last_reflection_successful = False
        assistant.reflection_error = str(e)
        assistant.can_retry_birth_reflection = True
        assistant.save(
            update_fields=[
                "last_reflection_attempted_at",
                "last_reflection_successful",
                "reflection_error",
                "can_retry_birth_reflection",
            ]
        )
        return None

    thought = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=text,
        thought_type="reflection",
        linked_memory=origin,
    )

    AssistantReflectionLog.objects.create(
        assistant=assistant,
        summary=text,
        title="Origin Reflection",
        linked_memory=origin,
        raw_prompt=prompt,
        category="meta",
    )
    log_trail_marker(assistant, "first_reflection", origin)

    assistant.save(
        update_fields=[
            "last_reflection_attempted_at",
            "last_reflection_successful",
            "reflection_error",
            "can_retry_birth_reflection",
        ]
    )

    return thought
