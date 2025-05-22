from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject
from assistants.utils.assistant_reflection_engine import (
    AssistantReflectionEngine,
    evaluate_thought_continuity,
)

@api_view(["POST"])
@permission_classes([AllowAny])
def evaluate_continuity(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    project_id = request.data.get("project_id")
    project = None
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id)
    engine = AssistantReflectionEngine(assistant)
    result = evaluate_thought_continuity(engine, project=project)
    return Response(result)
