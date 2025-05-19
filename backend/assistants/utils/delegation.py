"""Utilities for spawning delegated assistants."""

from __future__ import annotations

import uuid
from typing import Optional, Union

from assistants.models import (
    Assistant,
    ChatSession,
    DelegationEvent,
    AssistantObjective,
)
from assistants.helpers.reflection_helpers import reflect_on_delegation
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread
from project.models import Project


def spawn_delegated_assistant(
    parent_or_session: Union[Assistant, ChatSession],
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
) -> Assistant:
    """Create a child assistant inheriting context from the parent.

    The first argument may be a ``ChatSession`` or an ``Assistant`` instance.
    When a session is provided, the parent assistant, project and thread are
    derived automatically.
    """

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

    child = Assistant.objects.create(
        name=name or f"{parent.name} Delegate",
        description=description,
        specialty=specialty or parent.specialty,
        parent_assistant=parent,
        created_by=parent.created_by,
        preferred_model=parent.preferred_model,
    )

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
        reason=reason,
        summary=summary,
    )

    reflect_on_delegation(event)

    return child
