from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.models.trail import TrailMarkerLog
from memory.models import MemoryEntry
from assistants.utils.trail import get_trail_editable_fields


class AssistantTrailRecapView(APIView):
    """Return full trail recap data for an assistant."""

    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        markers = list(
            assistant.trail_markers.order_by("timestamp").values(
                "id",
                "marker_type",
                "timestamp",
                "notes",
                "user_note",
                "user_emotion",
                "is_starred",
            )
        )
        summary = (
            MemoryEntry.objects.filter(assistant=assistant, type="milestone_summary")
            .order_by("-created_at")
            .values("summary", "created_at")
            .first()
        )
        reflections = list(
            assistant.assistant_reflections.order_by("-created_at")
            .values("summary", "created_at")[:5]
        )
        stage_summaries = list(
            MemoryEntry.objects.filter(assistant=assistant, type="growth_summary")
            .order_by("created_at")
            .values("summary", "created_at", "event")
        )
        return Response(
            {
                "trail_markers": markers,
                "trail_summary": summary["summary"] if summary else None,
                "summary_created_at": summary["created_at"].isoformat() if summary else None,
                "reflections": reflections,
                "stage_summaries": [
                    {
                        "stage": int(s["event"].split()[1]) if s["event"] else None,
                        "summary": s["summary"],
                        "created_at": s["created_at"].isoformat(),
                    }
                    for s in stage_summaries
                ],
            }
        )


@api_view(["PATCH"])
def update_trail_marker(request, id):
    """Update user-facing fields on a TrailMarkerLog."""
    marker = get_object_or_404(TrailMarkerLog, id=id)
    editable = get_trail_editable_fields(marker, request.user)
    if not editable:
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    updates = {field: request.data.get(field) for field in editable if field in request.data}
    for field, value in updates.items():
        setattr(marker, field, value)
    if updates:
        marker.save(update_fields=list(updates.keys()))

    return Response(
        {
            "id": str(marker.id),
            "marker_type": marker.marker_type,
            "timestamp": marker.timestamp,
            "notes": marker.notes,
            "user_note": marker.user_note,
            "user_emotion": marker.user_emotion,
            "is_starred": marker.is_starred,
        }
    )

