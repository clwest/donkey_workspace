from __future__ import annotations

from django.utils import timezone
from datetime import datetime
from .logging_helper import log_trail_marker  # for reference (unused)
from assistants.models.trail import TrailMarkerLog
from memory.models import MemoryEntry


def summarize_trail_markers(assistant) -> MemoryEntry | None:
    """Create a milestone summary MemoryEntry for an assistant."""
    markers = (
        TrailMarkerLog.objects.filter(assistant=assistant)
        .order_by("timestamp")
        .select_related("related_memory")
    )
    if not markers.exists():
        return None

    segments = []
    for marker in markers:
        date_str = marker.timestamp.strftime("%B %d, %Y")
        if marker.marker_type == TrailMarkerLog.MarkerType.BIRTH:
            desc = f"{assistant.name} was born"
        elif marker.marker_type == TrailMarkerLog.MarkerType.PERSONALIZATION:
            desc = "received personalization"
        elif marker.marker_type == TrailMarkerLog.MarkerType.FIRST_CHAT:
            desc = "began chatting with users"
        elif marker.marker_type == TrailMarkerLog.MarkerType.FIRST_REFLECTION:
            desc = "reflected on its identity"
        else:
            desc = marker.marker_type.replace("_", " ")
        if marker.notes:
            desc += f" {marker.notes}".rstrip()
        if marker == markers.first():
            desc += f" on {date_str}"
        segments.append(desc)

    if len(segments) == 1:
        summary_text = segments[0]
    else:
        summary_text = ", then ".join(segments[:-1]) + ", and " + segments[-1]

    entry = MemoryEntry.objects.create(
        assistant=assistant,
        context=assistant.memory_context,
        event="Milestone summary",
        type="milestone_summary",
        summary=summary_text,
        is_summary=True,
        memory_type="milestone",
        source_role="assistant",
    )
    return entry
