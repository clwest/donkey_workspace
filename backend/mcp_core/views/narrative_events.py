from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from story.models import NarrativeEvent
from mcp_core.utils.scene_summary import summarize_scene_context


@api_view(["POST"])
@permission_classes([AllowAny])
def summarize_event(request, event_id):
    event = get_object_or_404(NarrativeEvent, id=event_id)
    summary = summarize_scene_context(event)
    return Response({"summary": summary})

