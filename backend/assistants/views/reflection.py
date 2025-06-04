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
from assistants.models.assistant import DelegationEvent
from assistants.models.thoughts import AssistantThoughtLog

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


@api_view(["GET"])
def subagent_reflect_view(request, event_id):
    """Return reflection on a delegated assistant's recent output."""
    event = (
        DelegationEvent.objects.select_related("child_assistant")
        .filter(id=event_id)
        .first()
    )
    if not event or not event.child_assistant:
        return Response({"error": "Delegation event not found"}, status=404)

    thoughts = list(
        AssistantThoughtLog.objects.filter(assistant=event.child_assistant)
        .order_by("-created_at")[:5]
    )

    if not thoughts:
        return Response({"summary": "No sub-agent output found."})

    summary = " | ".join(t.thought[:50] for t in thoughts)

    return Response(
        {
            "summary": summary,
            "linked_thoughts": [t.thought for t in thoughts],
            "assistant_slug": event.child_assistant.slug,
        }
    )
