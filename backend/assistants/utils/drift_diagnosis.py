import statistics
from collections import Counter
from typing import List, Dict

from memory.models import RAGPlaybackLog


def analyze_drift_symptoms(session_id: str) -> Dict[str, object]:
    """Return drift symptoms for a demo session."""
    logs = list(
        RAGPlaybackLog.objects.filter(demo_session_id=session_id).order_by("created_at")
    )
    total = len(logs)
    if total == 0:
        return {
            "fallback_rate": 0.0,
            "most_missed_terms": [],
            "average_anchor_score": 0.0,
            "diagnosis": [],
            "fallback_series": [],
        }

    fallback_series: List[int] = []
    missed_terms: List[str] = []
    anchor_scores: List[float] = []

    for pb in logs:
        pb_fallback = False
        has_anchor = False
        for c in pb.chunks:
            if c.get("is_fallback"):
                pb_fallback = True
            if c.get("anchor_match"):
                has_anchor = True
                anchor_scores.append(float(c.get("glossary_score", 0.0)))
        if pb_fallback:
            missed_terms.append(pb.query_term or pb.query)
        fallback_series.append(1 if pb_fallback else 0)

    fallback_rate = sum(fallback_series) / total
    avg_anchor_score = statistics.mean(anchor_scores) if anchor_scores else 0.0
    common = Counter([t for t in missed_terms if t]).most_common(2)
    most_missed = [term for term, _ in common]

    diagnosis: List[str] = []
    if avg_anchor_score < 0.2:
        diagnosis.append("⚠️ Anchor Drift Detected")
    if fallback_rate > 0.6:
        diagnosis.append("🔄 High Fallback Rate")
    if most_missed:
        diagnosis.append("🧠 Weak Glossary Coverage")

    return {
        "fallback_rate": round(fallback_rate, 2),
        "most_missed_terms": most_missed,
        "average_anchor_score": round(avg_anchor_score, 2),
        "diagnosis": diagnosis,
        "fallback_series": fallback_series,
    }
