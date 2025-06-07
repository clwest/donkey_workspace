from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from memory.models import MemoryEntry


class AssistantTrailRecapView(APIView):
    """Return full trail recap data for an assistant."""

    def get(self, request, slug):
        assistant = get_object_or_404(Assistant, slug=slug)
        markers = list(
            assistant.trail_markers.order_by("timestamp").values(
                "marker_type", "timestamp", "notes"
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
        return Response(
            {
                "trail_markers": markers,
                "trail_summary": summary["summary"] if summary else None,
                "summary_created_at": summary["created_at"].isoformat() if summary else None,
                "reflections": reflections,
            }
        )

