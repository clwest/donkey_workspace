from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.identity import IdentityAnchor
from assistants.models.mythpath import TemporalMythpathRecord, MythpathEvent


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_identity(request, id):
    assistant = get_object_or_404(Assistant, id=id)
    anchor, _ = IdentityAnchor.objects.get_or_create(
        assistant=assistant,
        defaults={"memory_origin": "", "codex_vector": {}},
    )
    data = {
        "assistant": str(assistant.id),
        "codex_vector": anchor.codex_vector,
        "memory_origin": anchor.memory_origin,
        "created_at": anchor.created_at,
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_mythpath(request, id):
    assistant = get_object_or_404(Assistant, id=id)
    record, _ = TemporalMythpathRecord.objects.get_or_create(assistant=assistant)
    events = MythpathEvent.objects.filter(assistant=assistant).order_by("created_at")
    return Response(
        {
            "assistant": str(assistant.id),
            "events": [
                {
                    "event_type": e.event_type,
                    "description": e.description,
                    "created_at": e.created_at,
                }
                for e in events
            ],
            "created_at": record.created_at,
        }
    )


class AssistantIdentitySummaryView(generics.GenericAPIView):
    """Return concise identity metadata for an assistant."""

    def get_object(self):
        return get_object_or_404(Assistant, slug=self.kwargs["slug"])

    def get_permissions(self):
        assistant = self.get_object()
        if assistant.is_demo:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get(self, request, slug):
        assistant = self.get_object()
        if not assistant.is_demo and assistant.created_by != request.user:
            return Response({"error": "forbidden"}, status=403)

        from assistants.serializers import AssistantSerializer

        serializer = AssistantSerializer(assistant, context={"request": request})
        return Response(serializer.data.get("identity_summary"))
