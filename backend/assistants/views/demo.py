from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.demo_config import DEMO_TIPS


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def demo_tips(request, slug):
    """Return demo walkthrough tips for a demo assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    if not assistant.is_demo:
        return Response({"tips": []})
    return Response({"tips": DEMO_TIPS})
