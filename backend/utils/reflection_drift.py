from collections import defaultdict
from typing import List, Dict
from django.utils import timezone
from datetime import timedelta

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor

__all__ = ["aggregate_drift_by_anchor"]

def aggregate_drift_by_anchor(assistant: Assistant, days: int | None = None) -> List[Dict[str, object]]:
    """Aggregate drifted reflection replays by anchor."""
    qs = ReflectionReplayLog.objects.filter(assistant=assistant).exclude(changed_anchors=[])
    if days:
        cutoff = timezone.now() - timedelta(days=days)
        qs = qs.filter(created_at__gte=cutoff)

    anchors = {a.slug: a.label for a in SymbolicMemoryAnchor.objects.all()}
    grouped: Dict[str, Dict[str, object]] = defaultdict(lambda: {
        "anchor_label": "",
        "scores": [],
        "reflections": [],
        "timestamp": None,
        "milestone_title": None,
    })

    for replay in qs.select_related("original_reflection__project"):
        drift = abs(replay.new_score - replay.old_score)
        for slug in replay.changed_anchors:
            label = anchors.get(slug, slug)
            info = grouped[slug]
            info["anchor_label"] = label
            info["scores"].append(drift)
            info["reflections"].append(str(replay.original_reflection_id))
            info["timestamp"] = replay.created_at if not info["timestamp"] or replay.created_at > info["timestamp"] else info["timestamp"]
            if replay.original_reflection and replay.original_reflection.project:
                milestone = replay.original_reflection.project.milestones.order_by("-created_at").first()
                if milestone:
                    info["milestone_title"] = milestone.title

    results = []
    for slug, data in grouped.items():
        avg_score = sum(data["scores"]) / len(data["scores"])
        results.append({
            "anchor_slug": slug,
            "anchor_label": data["anchor_label"],
            "avg_drift_score": round(avg_score, 2),
            "frequency": len(data["scores"]),
            "reflection_ids": data["reflections"],
            "timestamp": data["timestamp"],
            "milestone_title": data["milestone_title"],
        })
    results.sort(key=lambda r: r["avg_drift_score"], reverse=True)
    return results
