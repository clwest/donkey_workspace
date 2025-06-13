from django.db.models import Avg
from typing import List, Dict

from assistants.models.tooling import AssistantToolAssignment
from tools.models import ToolReflectionLog, ToolUsageLog, ToolConfidenceSnapshot

__all__ = ["summarize_tool_confidence"]


def summarize_tool_confidence(assistant) -> List[Dict[str, object]]:
    assignments = (
        AssistantToolAssignment.objects.filter(assistant=assistant)
        .select_related("tool")
    )
    results = []
    for a in assignments:
        avg_conf = (
            ToolReflectionLog.objects.filter(assistant=assistant, tool=a.tool)
            .aggregate(avg=Avg("confidence_score"))["avg"]
            or 0.0
        )
        usage = ToolUsageLog.objects.filter(assistant=assistant, tool=a.tool).count()
        ToolConfidenceSnapshot.objects.create(
            assistant=assistant,
            tool=a.tool,
            reflection_log=None,
            confidence_score=avg_conf,
            tags=[],
        )
        results.append(
            {
                "tool": a.tool.slug,
                "name": a.tool.name,
                "avg_confidence": round(avg_conf, 2),
                "usage_count": usage,
                "favorite": a.favorite,
            }
        )
    return sorted(results, key=lambda r: r["avg_confidence"], reverse=True)
