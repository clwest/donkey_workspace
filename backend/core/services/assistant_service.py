"""Assistant-related service functions."""

from __future__ import annotations

import uuid
from typing import Optional

from assistants.models.assistant import Assistant, ChatSession
from assistants.models.thoughts import AssistantThoughtLog
from project.models import Project
from prompts.models import Prompt
from mcp_core.models import NarrativeThread
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.helpers.reflection_helpers import reflect_on_delegation
from assistants.helpers.mood import get_session_mood, map_mood_to_tone
from memory.models import MemoryEntry
from tools.models import Tool


def create_assistant(
    *,
    name: str,
    description: str,
    specialty: str,
    prompt: Prompt,
    creator,
    parent_assistant: Optional[Assistant] = None,
    thread: Optional[NarrativeThread] = None,
) -> Assistant:
    """Create an assistant and bootstrap a project and session."""
    assistant = Assistant.objects.create(
        name=name,
        description=description,
        specialty=specialty,
        system_prompt=prompt,
        created_by=creator,
        preferred_model="gpt-4o",
        parent_assistant=parent_assistant,
    )

    project = Project.objects.create(
        user=creator,
        title=f"Auto Project for {assistant.name}",
        assistant=assistant,
        narrative_thread=thread,
        thread=thread,
        project_type="assistant",
        status="active",
    )
    ChatSession.objects.create(
        assistant=assistant,
        project=project,
        narrative_thread=thread,
        thread=thread,
        session_id=uuid.uuid4(),
    )

    log_assistant_thought(
        assistant,
        f"Assistant {assistant.name} created with specialty {assistant.specialty}",
        thought_type="planning",
        project=project,
    )

    return assistant


def spawn_delegated_assistant(
    parent_or_session: Assistant | ChatSession,
    project: Optional[Project] = None,
    *,
    name: Optional[str] = None,
    description: str = "",
    specialty: str = "",
    narrative_thread: Optional[NarrativeThread] = None,
    memory_entry: Optional[MemoryEntry] = None,
    reason: str = "delegation",
    summary: Optional[str] = None,
    objective: Optional["AssistantObjective"] = None,
    triggered_by_tool: Optional[Tool] = None,
) -> Assistant:
    """Create a delegated assistant inheriting context from the parent."""

    session = None
    thread = narrative_thread
    if isinstance(parent_or_session, ChatSession):
        session = parent_or_session
        parent = session.assistant
        if not project:
            project = session.project
        if not thread:
            thread = (
                session.thread
                or session.narrative_thread
                or (project.thread or project.narrative_thread if project else None)
            )
    else:
        parent = parent_or_session
        if not thread and project:
            thread = project.thread or project.narrative_thread

    if memory_entry and not thread:
        thread = (
            memory_entry.narrative_thread
            or (
                memory_entry.chat_session.thread
                if memory_entry.chat_session and memory_entry.chat_session.thread
                else (
                    memory_entry.chat_session.narrative_thread
                    if memory_entry.chat_session
                    else None
                )
            )
            or (
                memory_entry.related_project.thread
                if memory_entry.related_project and memory_entry.related_project.thread
                else (
                    memory_entry.related_project.narrative_thread
                    if memory_entry.related_project
                    else None
                )
            )
        )
        if not session:
            session = memory_entry.chat_session or session

    narrative_thread = thread

    if parent is None:
        raise ValueError("Parent assistant is required")

    mood = get_session_mood(session)
    tone = map_mood_to_tone(mood)

    child = Assistant.objects.create(
        name=name or f"{parent.name} Delegate",
        description=description,
        specialty=specialty or parent.specialty,
        parent_assistant=parent,
        created_by=parent.created_by,
        preferred_model=parent.preferred_model,
        created_from_mood=mood,
        inherited_tone=tone,
    )

    prompt = Prompt.objects.create(
        title=f"{child.name} Creation Prompt",
        content=(
            f"You are being created by a parent assistant currently feeling {mood}.\n"
            "Please respond with a tone that matches this mindset."
        ),
        type="system",
        tone=tone,
        source="delegation",
    )
    child.system_prompt = prompt
    child.save()

    child_project = Project.objects.create(
        user=parent.created_by,
        title=f"Project for {child.name}",
        assistant=child,
        narrative_thread=thread,
        thread=thread,
        project_type="assistant",
        status="active",
    )
    if narrative_thread is not None:
        child_project.thread = narrative_thread
        child_project.save()

    new_session = ChatSession.objects.create(
        assistant=child,
        project=child_project,
        narrative_thread=thread,
        thread=thread,
        session_id=uuid.uuid4(),
    )
    if narrative_thread is not None:
        new_session.thread = narrative_thread
        new_session.save()

    event = DelegationEvent.objects.create(
        parent_assistant=parent,
        child_assistant=child,
        triggering_memory=memory_entry,
        triggering_session=session,
        objective=objective,
        triggered_by_tool=triggered_by_tool,
        reason=reason,
        summary=summary,
    )

    reflect_on_delegation(event)

    return child
