from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models.assistant import Assistant
from agents.models.deployment import (
    AssistantDeploymentLog,
    DeploymentVector,
    ToolAssignment,
    SymbolicToolMap,
    AgentExecutionSession,
    PromptExecutionTrace,
    ToolOutcomeLedger,
)
from tools.models import Tool


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_deploy(request, assistant_id):
    """Preview or trigger a deployment for an assistant."""
    assistant = get_object_or_404(Assistant, id=assistant_id)

    if request.method == "POST":
        label = request.data.get("label", "")
        environment = request.data.get("environment", "ritual")
        AssistantDeploymentLog.objects.create(
            assistant=assistant, label=label, environment=environment
        )
        return Response({"status": "queued"})

    # Return a simple readiness preview
    skills = ["planning", "reflection", "execution"]
    readiness = {s: 1.0 for s in skills}
    return Response({"assistant": assistant.slug, "readiness": readiness})


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def assistant_toolchain(request, assistant_id):
    """Manage tool assignments for an assistant."""
    assistant = get_object_or_404(Assistant, id=assistant_id)

    if request.method == "POST":
        tool_ids = request.data.get("tools", [])
        assignment, _ = ToolAssignment.objects.get_or_create(assistant=assistant)
        if tool_ids:
            assignment.tools.set(Tool.objects.filter(id__in=tool_ids))
        return Response({"status": "saved"})

    tools = list(Tool.objects.filter(is_active=True).values("id", "name", "slug"))
    assigned = (
        ToolAssignment.objects.filter(assistant=assistant).first()
    )
    assigned_ids = list(assigned.tools.values_list("id", flat=True)) if assigned else []
    return Response({"tools": tools, "assigned": assigned_ids})


@api_view(["GET"])
@permission_classes([AllowAny])
def arena_active(request):
    """List active execution sessions."""
    sessions = AgentExecutionSession.objects.order_by("-created_at")[:20]
    data = []
    for s in sessions:
        traces = list(
            s.traces.all().values("id", "prompt", "result", "success")
        )
        data.append({
            "id": s.id,
            "assistant": s.assistant.slug,
            "status": s.status,
            "traces": traces,
        })
    return Response(data)
