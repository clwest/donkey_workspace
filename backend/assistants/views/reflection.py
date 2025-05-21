from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant, AssistantProject
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine

@api_view(["POST"])
@permission_classes([AllowAny])
def evaluate_continuity(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    project_id = request.data.get("project_id")
    project = None
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id)
    engine = AssistantReflectionEngine(assistant)
    result = engine.evaluate_thought_continuity(project=project)
    return Response(result)
