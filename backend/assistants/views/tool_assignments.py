from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from assistants.models.tooling import AssistantToolAssignment, AssistantTool
from assistants.utils.assistant_reflection_engine import reflect_on_tools
from tools.services.tool_confidence import summarize_tool_confidence
from django.core.management import call_command


@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_tools(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    assignments = AssistantToolAssignment.objects.filter(assistant=assistant)
    data = [
        {
            "tool": a.tool.name,
            "slug": a.tool.slug,
            "reason": a.reason,
            "score": a.confidence_score,
            "reflection": (
                a.reflection_log.summary if a.reflection_log else None
            ),
        }
        for a in assignments
    ]
    return Response({"tools": data})


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_tools(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    tool_slugs = request.data.get("tools", [])
    tools = list(AssistantTool.objects.filter(slug__in=tool_slugs))
    for tool in tools:
        AssistantToolAssignment.objects.get_or_create(
            assistant=assistant,
            tool=tool,
            defaults={"reason": "api", "confidence_score": 0.5},
        )
    log = reflect_on_tools(assistant)
    return Response(
        {"assigned": len(tools), "reflection": getattr(log, "summary", None)}
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_tools(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    log = reflect_on_tools(assistant)
    return Response({"summary": getattr(log, "summary", "")})


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_confidence(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    data = summarize_tool_confidence(assistant)
    return Response({"results": data})


@api_view(["POST"])
@permission_classes([AllowAny])
def recommend_tool_changes(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    call_command("update_tool_assignments")
    data = summarize_tool_confidence(assistant)
    return Response({"results": data})
