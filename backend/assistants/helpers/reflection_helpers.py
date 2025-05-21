from __future__ import annotations

from typing import Optional

from assistants.models import (
    DelegationEvent,
    AssistantThoughtLog,
    Assistant,
)
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from mcp_core.models import Tag
from memory.models import MemoryEntry, SimulatedMemoryFork


def reflect_on_delegation(
    delegation_event: DelegationEvent,
) -> Optional[AssistantThoughtLog]:
    """Generate and store a reflection about a ``DelegationEvent``."""
    parent = delegation_event.parent_assistant
    child = delegation_event.child_assistant

    project = None
    thread = None
    session = delegation_event.triggering_session
    memory = delegation_event.triggering_memory

    if session:
        project = session.project or project
        thread = session.narrative_thread or session.thread or thread
    if memory:
        if not project:
            project = memory.related_project or project
        if not thread:
            thread = memory.thread or memory.narrative_thread or thread

    details = [
        f"Delegated to {child.name}",
        f"Reason: {delegation_event.reason}",
    ]
    if delegation_event.objective:
        details.append(f"Objective: {delegation_event.objective.title}")
    if project:
        details.append(f"Project: {getattr(project, 'title', str(project))}")
    if thread:
        details.append(f"Thread: {thread.title}")
    if session:
        details.append(f"Session: {session.session_id}")
    if memory:
        snippet = memory.event[:50].replace("\n", " ")
        details.append(f"Memory: {snippet}")

    prompt = "\n".join(details) + "\nProvide a concise reflection on this delegation."

    engine = AssistantReflectionEngine(parent)
    try:
        reflection = engine.generate_reflection(prompt)
    except Exception:
        return None

    log = AssistantThoughtLog.objects.create(
        assistant=parent,
        project=project,
        narrative_thread=thread,
        thought=reflection,
        thought_type="reflection",
        thought_trace=f"delegation_event:{delegation_event.id}",
    )

    tag_objs = []
    for name in ["delegation", "auto-reflection"]:
        tag, _ = Tag.objects.get_or_create(slug=name, defaults={"name": name})
        tag_objs.append(tag)
    if tag_objs:
        log.tags.add(*tag_objs)

    return log


def simulate_memory_fork(
    assistant: Assistant,
    memory: MemoryEntry,
    alternative_action: str | None = None,
    notes: str | None = None,
) -> SimulatedMemoryFork:
    """Generate a hypothetical outcome for an alternate decision."""

    details = [f"Original: {memory.event}"]
    if alternative_action:
        details.append(f"Hypothetical action: {alternative_action}")
    if notes:
        details.append(f"Notes: {notes}")

    prompt = "\n".join(details) + "\nPredict the alternate outcome succinctly."

    engine = AssistantReflectionEngine(assistant)
    try:
        outcome = engine.generate_reflection(prompt)
    except Exception:
        outcome = "Simulation failed"

    thought = AssistantThoughtLog.objects.create(
        assistant=assistant,
        thought=outcome,
        thought_type="reflection",
        linked_memory=memory,
        event="simulated_memory_fork",
    )

    fork = SimulatedMemoryFork.objects.create(
        original_memory=memory,
        assistant=assistant,
        simulated_outcome=outcome,
        hypothetical_action=alternative_action,
        reason_for_simulation=notes or "",
        thought_log=thought,
    )

    return fork
