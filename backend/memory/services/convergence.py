from django.db.models import Avg, Count, Max, Q
from .reinforcement import reinforce_glossary_anchor  # for potential reuse
from ..models import SymbolicMemoryAnchor, RAGGroundingLog

__all__ = ["calculate_convergence_stats", "recalculate_anchor_convergence"]


def calculate_convergence_stats(anchor: SymbolicMemoryAnchor) -> dict:
    """Return convergence metrics for an anchor."""
    qs = RAGGroundingLog.objects.filter(expected_anchor=anchor.slug)
    if anchor.assistant_id:
        qs = qs.filter(assistant_id=anchor.assistant_id)

    agg = qs.aggregate(
        avg_score=Avg("adjusted_score"),
        fallback_count=Count("id", filter=Q(fallback_triggered=True)),
        glossary_boost=Avg("glossary_boost_applied"),
        last_updated=Max("created_at"),
        total=Count("id"),
    )
    total = agg.get("total") or 0
    fallback_count = agg.get("fallback_count") or 0
    avg = agg.get("avg_score") or 0.0
    mutation_score = avg * (1 - (fallback_count / total)) if total else 0.0
    agg["mutation_score"] = round(mutation_score, 2)
    return agg


def recalculate_anchor_convergence(anchor: SymbolicMemoryAnchor) -> dict:
    """Recalculate and store anchor convergence stats."""
    stats = calculate_convergence_stats(anchor)
    anchor.avg_score = stats.get("avg_score") or 0.0
    anchor.save(update_fields=["avg_score"])
    return stats
