from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.models.demo_usage import DemoUsageLog
from assistants.demo_config import DEMO_TIPS


def bump_demo_score(session_id, delta=0, helpful=False):
    try:
        log = DemoUsageLog.objects.get(session_id=session_id)
    except DemoUsageLog.DoesNotExist:
        return
    log.demo_interaction_score += delta
    if helpful:
        log.tips_helpful += 1
    if log.demo_interaction_score >= 15:
        log.likely_to_convert = True
    fields = ["demo_interaction_score", "likely_to_convert"]
    if helpful:
        fields.append("tips_helpful")
    log.save(update_fields=fields)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def demo_tips(request, slug):
    """Return demo walkthrough tips for a demo assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    if not assistant.is_demo:
        return Response({"tips": []})

    session_id = request.data.get("session_id") or request.query_params.get(
        "session_id"
    )

    if request.method == "GET":
        if session_id:
            bump_demo_score(session_id, 2)
        return Response({"tips": DEMO_TIPS})

    if request.method == "PATCH":
        tip_id = request.data.get("tip_id")
        helpful = bool(request.data.get("helpful"))
        if session_id and helpful and tip_id:
            bump_demo_score(session_id, 5, helpful=True)
        return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_recap(request, session_id):
    log = get_object_or_404(DemoUsageLog, session_id=session_id)
    data = {
        "score": log.demo_interaction_score,
        "tips_helpful": log.tips_helpful,
        "messages_sent": log.message_count,
        "starter_query": log.starter_query,
        "demo_slug": log.assistant.demo_slug,
        "suggested_name": log.assistant.name.replace("Demo", "").strip()
        or log.assistant.name,
        "converted": log.converted_to_real_assistant,
    }
    return Response(data)
