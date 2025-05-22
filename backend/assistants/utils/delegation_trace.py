from __future__ import annotations

from typing import List

from assistants.models.assistant import Assistant, DelegationEvent
from memory.models import MemoryEntry


def build_delegation_trace(assistant: Assistant, depth: int = 0) -> List[MemoryEntry]:
    """Return memory entries across a delegation chain annotated with depth."""
    entries: List[MemoryEntry] = []
    mems = MemoryEntry.objects.filter(assistant=assistant).order_by("created_at")
    for m in mems:
        m.depth = depth
        m.is_delegated = assistant.parent_assistant_id is not None
        m.assistant_name = assistant.name
        m.assistant_id = assistant.id
        m.parent_assistant_name = (
            assistant.parent_assistant.name if assistant.parent_assistant else None
        )
        event = DelegationEvent.objects.filter(triggering_memory=m).first()
        m.delegation_event_id = event.id if event else None
        entries.append(m)

    child_events = DelegationEvent.objects.filter(parent_assistant=assistant).select_related(
        "child_assistant"
    )
    for event in child_events:
        entries.extend(build_delegation_trace(event.child_assistant, depth + 1))
    return entries
