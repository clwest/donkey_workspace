from typing import List, Dict
from django.db.models import Avg
from assistants.models import Assistant
from memory.models import (
    SymbolicMemoryAnchor,
    RAGGroundingLog,
    AnchorDriftLog,
)

__all__ = ["get_anchor_health_metrics"]


def get_anchor_health_metrics(assistant: Assistant) -> List[Dict[str, object]]:
    """Return anchor health metrics for an assistant."""
    anchors = SymbolicMemoryAnchor.objects.filter(
        memory_context=assistant.memory_context
    ).order_by("slug")
    metrics = []
    for a in anchors:
        logs = RAGGroundingLog.objects.filter(
            assistant=assistant, expected_anchor=a.slug
        )
        avg_score = logs.aggregate(avg=Avg("adjusted_score")).get("avg") or 0.0
        fallback_count = logs.filter(fallback_triggered=True).count()
        reinforcement_count = a.reinforcement_logs.filter(assistant=assistant).count()
        total_chunks = a.chunks.count()
        drifted = a.chunks.filter(is_drifting=True).count()
        drift_score = drifted / total_chunks if total_chunks else 0.0
        drift_logs = list(a.drift_logs.order_by("-observation_date")[:7][::-1])
        trend = [dl.avg_score for dl in drift_logs]
        slope = 0.0
        if len(trend) > 1:
            slope = (trend[-1] - trend[0]) / (len(trend) - 1)
        metrics.append(
            {
                "label": a.label,
                "slug": a.slug,
                "avg_score": round(avg_score, 2),
                "fallback_count": fallback_count,
                "mutation_status": a.mutation_status,
                "reinforcement_count": reinforcement_count,
                "chunk_count": total_chunks,
                "drift_score": round(drift_score, 2),
                "score_slope": round(slope, 3),
                "trend": trend,
            }
        )
    return metrics
