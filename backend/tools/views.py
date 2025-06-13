from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Tool, ToolUsageLog, ToolExecutionLog
from tools.utils.tool_registry import execute_tool
from tools.utils import mutate_prompt_based_on_tool_feedback
from assistants.models.reflection import AssistantReflectionLog


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_list(request):
    tools = Tool.objects.filter(is_active=True, is_enabled=True)
    data = [
        {
            "name": t.name,
            "slug": t.slug,
            "description": t.description,
            "input_schema": t.input_schema,
            "output_schema": t.output_schema,
            "tags": t.tags,
        }
        for t in tools
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_detail(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    data = {
        "id": tool.id,
        "name": tool.name,
        "slug": tool.slug,
        "description": tool.description,
        "version": tool.version,
        "code_reference": tool.code_reference,
        "input_schema": tool.input_schema,
        "output_schema": tool.output_schema,
        "is_public": tool.is_public,
        "enabled": tool.enabled,
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def invoke_tool(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    payload = request.data or {}
    result = None
    success = True
    error = ""
    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    assistant_ident = payload.get("assistant_id")
    if assistant_ident:
        try:
            payload["assistant_id"] = str(
                resolve_or_error(assistant_ident, Assistant).id
            )
        except ObjectDoesNotExist:
            payload["assistant_id"] = None

    try:
        result = execute_tool(tool, payload)
    except Exception as e:
        success = False
        error = str(e)

    ToolUsageLog.objects.create(
        tool=tool,
        assistant_id=payload.get("assistant_id"),
        agent_id=payload.get("agent_id"),
        success=success,
        error=error if not success else "",
        input_payload=payload,
        output_payload=result if success else None,
    )

    status_code = 200 if success else 500
    return Response(
        {"result": result, "success": success, "error": error}, status=status_code
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def execute_tool_view(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    payload = request.data or {}
    result = None
    success = True
    error = ""
    status_code = 200
    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    assistant_ident = payload.get("assistant_id")
    if assistant_ident:
        try:
            payload["assistant_id"] = str(
                resolve_or_error(assistant_ident, Assistant).id
            )
        except ObjectDoesNotExist:
            payload["assistant_id"] = None

    try:
        result = execute_tool(tool, payload)
    except Exception as e:  # pragma: no cover - simple logging
        success = False
        error = str(e)
        status_code = 500

    ToolExecutionLog.objects.create(
        tool=tool,
        assistant_id=payload.get("assistant_id"),
        agent_id=payload.get("agent_id"),
        input_data=payload,
        output_data=result if success else None,
        success=success,
        status_code=status_code,
        error_message=error,
    )

    return Response(
        {"result": result, "success": success, "error": error}, status=status_code
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_tool_feedback(request, id):
    """Record feedback on a tool usage log and trigger prompt mutation."""
    log = get_object_or_404(ToolUsageLog, id=id)
    feedback = request.data.get("feedback")
    message = request.data.get("message", "")
    if feedback not in dict(ToolUsageLog.FEEDBACK_CHOICES):
        return Response({"error": "Invalid feedback"}, status=400)
    log.feedback = feedback
    log.save(update_fields=["feedback"])

    if log.assistant:
        mutate_prompt_based_on_tool_feedback(log, feedback, log.assistant, message)
        if message:
            AssistantReflectionLog.objects.create(
                assistant=log.assistant,
                title="Tool Feedback",
                summary=message,
            )

    return Response({"status": "saved"})


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_logs(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    logs = ToolExecutionLog.objects.filter(tool=tool)[:50]
    data = [
        {
            "id": log.id,
            "assistant": log.assistant_id,
            "agent": log.agent_id,
            "input_data": log.input_data,
            "output_data": log.output_data,
            "success": log.success,
            "status_code": log.status_code,
            "error_message": log.error_message,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_reflections(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    from tools.models import ToolReflectionLog

    logs = ToolReflectionLog.objects.filter(tool=tool).order_by("-created_at")[:50]
    data = [
        {
            "id": r.id,
            "assistant": r.assistant.slug if r.assistant else None,
            "reflection": r.reflection,
            "confidence_score": r.confidence_score,
            "tags": list(r.insight_tags.values_list("slug", flat=True)),
            "created_at": r.created_at.isoformat(),
        }
        for r in logs
    ]
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_tool_now(request, pk):
    tool = get_object_or_404(Tool, pk=pk)
    from assistants.utils.assistant_reflection_engine import reflect_on_tool_usage

    assistants = list(
        ToolExecutionLog.objects.filter(tool=tool)
        .values_list("assistant_id", flat=True)
        .distinct()
    )
    from assistants.models import Assistant

    total = 0
    for aid in assistants:
        if not aid:
            continue
        assistant = Assistant.objects.filter(id=aid).first()
        if assistant:
            logs = reflect_on_tool_usage(assistant)
            total += sum(1 for l in logs if l.tool_id == tool.id)
    return Response({"created": total})


@api_view(["GET"])
@permission_classes([AllowAny])
def tool_index(request):
    """Return summary details for all tools."""
    from assistants.models.tooling import AssistantToolAssignment
    from tools.models import ToolReflectionLog

    qs = Tool.objects.all()
    assistant = request.GET.get("assistant")
    tool_type = request.GET.get("type")
    if assistant:
        qs = qs.filter(
            slug__in=AssistantToolAssignment.objects.filter(
                assistant__slug=assistant
            ).values_list("tool__slug", flat=True)
        )
    if tool_type:
        qs = qs.filter(tags__contains=[tool_type])
    results = []
    for tool in qs:
        last_exec = (
            ToolExecutionLog.objects.filter(tool=tool).order_by("-created_at").first()
        )
        exec_count = ToolExecutionLog.objects.filter(tool=tool).count()
        assistants = list(
            AssistantToolAssignment.objects.filter(tool__slug=tool.slug)
            .select_related("assistant")
            .values_list("assistant__slug", flat=True)
        )
        reflections = ToolReflectionLog.objects.filter(tool=tool).order_by(
            "-created_at"
        )[:5]
        results.append(
            {
                "id": tool.id,
                "name": tool.name,
                "slug": tool.slug,
                "version": tool.version,
                "is_public": tool.is_public,
                "last_used_at": last_exec.created_at.isoformat() if last_exec else None,
                "exec_count": exec_count,
                "assistants": assistants,
                "recent_reflections": [
                    {
                        "id": r.id,
                        "assistant": r.assistant.slug,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in reflections
                ],
            }
        )
    return Response({"results": results})
