from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from assistants.models import Assistant, AssistantHintState
from assistants.hint_config import HINTS
from assistants.utils.hints import get_next_hint_for_user


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
    obj.completed_at = timezone.now()
    obj.save()
    return Response({"status": "dismissed"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tour_progress(request, slug):
    """Return progress data for the assistant's hint tour."""
    assistant = get_object_or_404(Assistant, slug=slug)
    states = AssistantHintState.objects.filter(user=request.user, assistant=assistant)
    completed = {s.hint_id for s in states if s.completed_at}
    total = len(HINTS)
    next_hint = get_next_hint_for_user(assistant, request.user)
    percent = int((len(completed) / total) * 100) if total else 0
    return Response(
        {
            "total": total,
            "completed": len(completed),
            "next_hint": next_hint,
            "percent_complete": percent,
        }
    )
