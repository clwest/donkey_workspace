from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
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
