from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


from assistants.models import Assistant, DemoUsageLog

from assistants.demo_config import DEMO_TIPS
from assistants.helpers.demo_utils import (
    generate_assistant_from_demo,
    boost_prompt_from_demo,
)


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

    return Response({"tips": DEMO_TIPS})


@api_view(["POST"])
@permission_classes([IsAdminUser])
def replay_demo_boost(request):
    """Clone a demo session and run the boost routine."""
    session_id = request.data.get("demo_session_id")
    if not session_id:
        return Response({"error": "demo_session_id required"}, status=400)
    log = get_object_or_404(DemoUsageLog, session_id=session_id)
    from assistants.utils.session_utils import load_session_messages

    transcript = load_session_messages(session_id)
    assistant = generate_assistant_from_demo(
        log.assistant.demo_slug, request.user, transcript
    )
    summary = boost_prompt_from_demo(assistant, transcript)
    return Response({"slug": assistant.slug, "summary": summary})

