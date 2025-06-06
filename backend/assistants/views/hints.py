from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from assistants.models import Assistant, AssistantHintState
from assistants.hint_config import HINTS


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_hint_list(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    states = AssistantHintState.objects.filter(user=request.user, assistant=assistant)
    state_map = {s.hint_id: s for s in states}
    hints = []
    for h in HINTS:
        s = state_map.get(h["id"])
        hints.append(
            {
                "id": h["id"],
                "label": h.get("label", ""),
                "content": h.get("content", ""),
                "dismissed": getattr(s, "dismissed", False),
                "seen_at": s.seen_at.isoformat() if s else None,
            }
        )
    return Response({"hints": hints})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def dismiss_hint(request, slug, hint_id):
    assistant = get_object_or_404(Assistant, slug=slug)
    obj, _ = AssistantHintState.objects.get_or_create(
        user=request.user, assistant=assistant, hint_id=hint_id
    )
    obj.dismissed = True
    obj.seen_at = timezone.now()
    obj.save()
    return Response({"status": "dismissed"})
