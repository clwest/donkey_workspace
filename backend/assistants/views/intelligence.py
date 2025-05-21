from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant, AssistantProject
from mcp_core.models import NarrativeThread
from assistants.serializers import AssistantNextActionSerializer
from assistants.utils.assistant_reflection_engine import plan_from_thread_context


@api_view(["POST"])
@permission_classes([AllowAny])
def plan_from_thread(request, slug):
    """Generate next actions for a narrative thread."""
    assistant = get_object_or_404(Assistant, slug=slug)
    thread_id = request.data.get("thread_id")
    if not thread_id:
        return Response({"error": "thread_id required"}, status=400)
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    project = None
    project_id = request.data.get("project_id")
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id)

    actions = plan_from_thread_context(thread, assistant, project)
    serializer = AssistantNextActionSerializer(actions, many=True)
    return Response(serializer.data)
