from typing import List, Dict
from django.db.models import Avg, F
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorConfidenceLog

__all__ = ["get_anchor_confidence"]


def get_anchor_confidence(assistant: Assistant) -> List[Dict[str, object]]:
    """Return latest confidence metrics for anchors."""
    anchors = SymbolicMemoryAnchor.objects.filter(memory_context=assistant.memory_context).order_by("slug")
    results = []
    for a in anchors:
        log = AnchorConfidenceLog.objects.filter(anchor=a).order_by("-created_at").first()
        if not log:
            continue
        results.append(
            {
                "label": a.label,
                "slug": a.slug,
                "avg_score": round(log.avg_score, 2),
                "fallback_rate": round(log.fallback_rate, 2),
                "glossary_hit_pct": round(log.glossary_hit_pct, 2),
            }
        )
    return results
