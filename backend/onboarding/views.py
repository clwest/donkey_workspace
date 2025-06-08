from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import (
    record_step_completion,
    get_onboarding_status,
    get_next_onboarding_step,
    get_progress_percent,
    generate_guide_reply,
    get_alias_map,
)
from .guide_logic import get_hint_status, suggest_next_hint
from assistants.models import Assistant
from django.utils import timezone
from mcp_core.models import PublicEventLog
from .config import ONBOARDING_WORLD
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from memory.services.acquisition import update_anchor_acquisition
from django.shortcuts import get_object_or_404
from assistants.helpers.logging_helper import log_trail_marker


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def onboarding_intro(request):
    """Return intro data or dismiss the intro."""
    if request.method == "POST":
        request.user.dismissed_onboarding_intro = True
        request.user.save(update_fields=["dismissed_onboarding_intro"])
        return Response({"status": "dismissed"})

    steps = [
        {
            "slug": n["slug"],
            "name": n["title"],
            "emoji": n.get("emoji", ""),
            "goal": n.get("goal", n.get("description", "")),
            "ui_label": n.get("ui_label"),
            "tooltip": n.get("tooltip"),
        }
        for n in ONBOARDING_WORLD["nodes"]
    ]
    data = {
        "title": ONBOARDING_WORLD["title"],
        "welcome": ONBOARDING_WORLD.get(
            "welcome", "Welcome to the MythOS Onboarding World!"
        ),
        "steps": steps,
        "video": ONBOARDING_WORLD.get("video"),
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    theme = request.query_params.get("theme", "fantasy")
    aliases = get_alias_map(theme)

    show_intro = (
        next_step == "world" and not getattr(request.user, "dismissed_onboarding_intro", False)
    )
    return Response({
        "progress": progress,
        "next_step": next_step,
        "percent": percent,
        "show_intro": show_intro,
        "aliases": aliases,
    })



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def onboarding_complete(request):
    if get_next_onboarding_step(request.user) is None:
        return Response({"onboarding_complete": True})

    step = request.data.get("step")
    if step:
        record_step_completion(request.user, step)
    else:
        for s in ONBOARDING_WORLD["nodes"]:
            record_step_completion(request.user, s["slug"])
    if not Assistant.objects.filter(created_by=request.user).exists():
        Assistant.objects.create(
            name="My Assistant",
            description="Default assistant",
            created_by=request.user,
        )
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    if next_step is None and not request.user.onboarding_complete:
        request.user.onboarding_complete = True
        request.user.save(update_fields=["onboarding_complete"])
    return Response(
        {
            "progress": progress,
            "next_step": next_step,
            "percent": percent,
            "onboarding_complete": next_step is None,
            "redirect": "/assistants/primary/dashboard",
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def onboarding_node_detail(request, step):
    node = next((n for n in ONBOARDING_WORLD["nodes"] if n["slug"] == step), None)
    if not node:
        return Response({"error": "not found"}, status=404)
    return Response(node)


@api_view(["GET"])
@permission_classes([AllowAny])
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def guide_chat(request):
    """Return onboarding guide responses or record dismissal."""
    if request.data.get("dismiss"):
        request.user.dismissed_guide = True
        request.user.save(update_fields=["dismissed_guide"])
        return Response({"status": "dismissed"})
    message = request.data.get("message", "").strip()
    if not message:
        return Response({"error": "message required"}, status=400)
    hint_status = get_hint_status(request.user)
    reply = generate_guide_reply(message, hint_status=hint_status)
    hint_id, action = suggest_next_hint(request.user)
    data = {"reply": reply}
    if hint_id:
        data["hint_suggestion"] = hint_id
    if action:
        data["ui_action"] = action
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ritual_complete(request):
    """Finalize onboarding and return assistant slug."""
    assistant = (
        Assistant.objects.filter(created_by=request.user)
        .order_by("-created_at")
        .first()
    )
    if not assistant:
        return Response({"error": "assistant not found"}, status=404)
    assistant.is_guide = False
    if hasattr(assistant, "onboarding_complete"):
        assistant.onboarding_complete = True
    if hasattr(assistant, "capstone_completed_at"):
        assistant.capstone_completed_at = timezone.now()
    assistant.save()
    record_step_completion(request.user, "ritual")
    log_trail_marker(assistant, "personalization")
    PublicEventLog.objects.create(
        actor_name=request.user.username,
        event_details="onboarding_step=capstone_complete",
    )
    return Response({"slug": assistant.slug})
