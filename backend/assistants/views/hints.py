from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from assistants.utils.starter_chat import seed_chat_starter_memory


def _get_demo_assistant(user):
    """Return or create a placeholder Assistant record for demo hints."""
    assistant, _ = Assistant.objects.get_or_create(
        slug="demo",
        defaults={
            "name": "Demo",
            "description": "Placeholder for demo hints",
            "specialty": "demo",
            "created_by": user,
        },
    )
    if not assistant.memories.exists():
        seed_chat_starter_memory(assistant)
    return assistant

from assistants.models import (
    Assistant,
    AssistantHintState,
    AssistantTourStartLog,
)
from assistants.hint_config import HINTS
from assistants.utils.hints import get_next_hint_for_user
from onboarding.guide_logic import get_hint_status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_hint_list(request, slug):
    if slug == "demo":
        assistant = _get_demo_assistant(request.user)
    else:
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
    if slug == "demo":
        assistant = _get_demo_assistant(request.user)
    else:
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def tour_started(request, slug):
    """Mark that the hint tour has started for this assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    obj, created = AssistantTourStartLog.objects.get_or_create(
        user=request.user,
        assistant=assistant,
        defaults={"source": request.data.get("source", "dashboard")},
    )
    hint_status = get_hint_status(request.user)
    return Response({"started": True, "created": created, "hint_status": hint_status})
