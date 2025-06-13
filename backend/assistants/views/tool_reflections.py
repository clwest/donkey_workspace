from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from assistants.models import Assistant
from tools.models import ToolReflectionLog, ToolExecutionLog, Tool
from assistants.utils.assistant_reflection_engine import reflect_on_tool_usage
from django.db.models import Count, Avg

@api_view(["GET"])
@permission_classes([AllowAny])
def assistant_tool_reflections(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    usage_counts = (
        ToolExecutionLog.objects.filter(assistant=assistant)
        .values("tool_id")
        .annotate(count=Count("id"))
    )
    reflections = ToolReflectionLog.objects.filter(assistant=assistant)
    data = []
    for u in usage_counts:
        tool = Tool.objects.get(id=u["tool_id"])
        logs = reflections.filter(tool=tool)
        avg_conf = logs.aggregate(avg=Avg("confidence_score"))["avg"] or 0.0
        tags = list(
            logs.values_list("insight_tags__slug", flat=True).distinct()
        )
        summary = logs.first().reflection if logs.exists() else ""
        data.append(
            {
                "tool": {"id": tool.id, "name": tool.name, "slug": tool.slug},
                "usage_count": u["count"],
                "confidence": avg_conf,
                "summary": summary,
                "tags": tags,
            }
        )
    return Response(data)

*** End ***
