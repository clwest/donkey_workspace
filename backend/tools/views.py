from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Tool, ToolUsageLog
from tools.utils.tool_registry import execute_tool
from tools.utils import mutate_prompt_based_on_tool_feedback
from assistants.models import AssistantReflectionLog


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


@api_view(["POST"])
@permission_classes([AllowAny])
def invoke_tool(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    payload = request.data or {}
    result = None
    success = True
    error = ""
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
