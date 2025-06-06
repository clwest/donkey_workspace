from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import (
    record_step_completion,
    get_onboarding_status,
    get_next_onboarding_step,
    get_progress_percent,
)
from .config import ONBOARDING_WORLD
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from memory.services.acquisition import update_anchor_acquisition
from django.shortcuts import get_object_or_404


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    return Response({"progress": progress, "next_step": next_step, "percent": percent})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def onboarding_complete(request):
    step = request.data.get("step")
    if not step:
        return Response({"error": "step required"}, status=400)
    record_step_completion(request.user, step)
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    return Response({"progress": progress, "next_step": next_step, "percent": percent})


@api_view(["GET"])
@permission_classes([AllowAny])
def onboarding_node_detail(request, step):
    node = next((n for n in ONBOARDING_WORLD["nodes"] if n["slug"] == step), None)
    if not node:
        return Response({"error": "not found"}, status=404)
    return Response(node)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_boot(request):
    """Return a few sample anchors for onboarding."""
    anchors = (
        SymbolicMemoryAnchor.objects.order_by("-fallback_score")[:3]
        or SymbolicMemoryAnchor.objects.all()[:3]
    )
    data = [
        {
            "slug": a.slug,
            "label": a.label,
            "description": a.description,
        }
        for a in anchors
    ]
    return Response({"results": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def teach_anchor(request):
    """Mark an anchor as taught and log a memory entry."""
    slug = request.data.get("anchor_slug")
    if not slug:
        return Response({"error": "anchor_slug required"}, status=400)
    anchor = get_object_or_404(SymbolicMemoryAnchor, slug=slug)
    MemoryEntry.objects.create(
        event=
            f'User chose to teach the assistant the anchor "{anchor.label}" '
            f'meaning {anchor.description}. This is a foundational term.',
        anchor=anchor,
        source_role="user",
        source_user=request.user,
        assistant=anchor.assistant,
    )
    update_anchor_acquisition(anchor, "acquired")
    return Response({"status": "ok"})
