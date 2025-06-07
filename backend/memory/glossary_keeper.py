from __future__ import annotations

from datetime import timedelta
from typing import Optional, Tuple

from django.utils import timezone

from .models import (
    SymbolicMemoryAnchor,
    RAGGroundingLog,
    AnchorReinforcementLog,
    MemoryEntry,
    GlossaryKeeperLog,
)
from mcp_core.models import Tag
from utils.llm import call_gpt4

__all__ = [
    "run_keeper_tasks",
    "calculate_anchor_drift",
    "suggest_mutation_with_rationale",
    "reflect_on_anchor_drift",
    "log_keeper_action",
    "promote_stable_anchor",
    "score_drift_priority",
]

DEFAULT_FALLBACK_LIMIT = 5
STALE_DAYS = 30


def calculate_anchor_drift(anchor: SymbolicMemoryAnchor) -> float:
    """Return drift score based on drifting chunks."""
    total = anchor.chunks.count()
    drifted = anchor.chunks.filter(is_drifting=True).count()
    return drifted / total if total else 0.0


def suggest_mutation_with_rationale(anchor: SymbolicMemoryAnchor) -> Tuple[str, str]:
    """Ask GPT for a better anchor label with a short rationale."""
    prompt = (
        f"The glossary term '{anchor.label}' is losing clarity. "
        "Suggest a concise replacement and briefly explain why."
    )
    suggestion = call_gpt4(prompt)
    cleaned = suggestion.strip().strip('"').strip(".")
    rationale = f"Replacement suggested for drifted term {anchor.label}."
    return cleaned or anchor.label, rationale


def reflect_on_anchor_drift(
    anchor: SymbolicMemoryAnchor, rationale: str, assistant=None
) -> MemoryEntry:
    """Create a memory entry describing anchor drift."""
    summary = f"Anchor {anchor.label} drifting: {rationale}"
    mem = MemoryEntry.objects.create(
        assistant=assistant or anchor.assistant,
        anchor=anchor,
        context=anchor.memory_context,
        summary=summary,
        event=summary,
        type="reflection",
    )
    tag, _ = Tag.objects.get_or_create(
        slug="glossary_drift", defaults={"name": "glossary_drift"}
    )
    mem.tags.add(tag)
    return mem


def log_keeper_action(
    *,
    anchor: SymbolicMemoryAnchor,
    assistant=None,
    action_taken: str,
    score_before: Optional[float] = None,
    score_after: Optional[float] = None,
    notes: str = "",
) -> GlossaryKeeperLog:
    return GlossaryKeeperLog.objects.create(
        anchor=anchor,
        assistant=assistant or anchor.assistant,
        action_taken=action_taken,
        score_before=score_before,
        score_after=score_after,
        notes=notes,
    )


def score_drift_priority(anchor: SymbolicMemoryAnchor) -> float:
    """Return a drift priority score for sorting anchors."""
    drift = calculate_anchor_drift(anchor)
    reflection_freq = anchor.related_reflections.count()
    missed = RAGGroundingLog.objects.filter(
        expected_anchor=anchor.slug, fallback_triggered=True
    ).count()
    pending = 1.0 if anchor.mutation_status == "pending" else 0.0
    score = drift + 0.1 * reflection_freq + 0.3 * missed + pending
    return round(score, 2)


def promote_stable_anchor(anchor: SymbolicMemoryAnchor) -> bool:
    """Auto-promote anchor if drift is stable and reinforced."""
    logs = anchor.keeper_logs.filter(action_taken="priority_scored").order_by(
        "-timestamp"
    )[:5]
    if len(logs) < 5:
        return False
    if any((log.score_before or 0) >= 0.15 for log in logs):
        return False
    if anchor.reinforcement_logs.count() <= 3:
        return False
    if anchor.mutation_status != "pending":
        return False

    anchor.label = anchor.suggested_label or anchor.label
    anchor.mutation_status = "applied"
    anchor.is_stable = True
    anchor.stabilized_at = timezone.now()
    anchor.save(
        update_fields=["label", "mutation_status", "is_stable", "stabilized_at"]
    )
    log_keeper_action(anchor=anchor, action_taken="auto_promote")
    return True


def run_keeper_tasks(
    assistant: Optional[object] = None,
    *,
    dry_run: bool = False,
    limit: Optional[int] = None,
    min_drift: float = 0.5,
    auto_promote: bool = False,
    drift_top: Optional[int] = None,
):
    """Scan anchors and create mutation suggestions or reflections."""
    qs = SymbolicMemoryAnchor.objects.all().order_by("slug")
    if assistant:
        qs = qs.filter(assistant=assistant)
    anchors = []
    for anchor in qs:
        priority = score_drift_priority(anchor)
        anchor.drift_priority_score = priority
        anchor.save(update_fields=["drift_priority_score"])
        log_keeper_action(
            anchor=anchor,
            assistant=assistant,
            action_taken="priority_scored",
            score_before=calculate_anchor_drift(anchor),
            score_after=priority,
        )
        anchors.append(anchor)

    anchors.sort(key=lambda a: a.drift_priority_score, reverse=True)
    if drift_top:
        anchors = anchors[:drift_top]

    processed = 0
    for anchor in anchors:
        if limit and processed >= limit:
            break
        drift = calculate_anchor_drift(anchor)
        fallbacks = RAGGroundingLog.objects.filter(
            expected_anchor=anchor.slug,
            fallback_triggered=True,
        )
        fallback_count = fallbacks.count()
        last_log = (
            AnchorReinforcementLog.objects.filter(anchor=anchor)
            .order_by("-created_at")
            .first()
        )
        stale = False
        if last_log:
            stale = timezone.now() - last_log.created_at > timedelta(days=STALE_DAYS)
        if drift < min_drift and fallback_count <= DEFAULT_FALLBACK_LIMIT and not stale:
            continue
        suggestion, rationale = suggest_mutation_with_rationale(anchor)
        if not dry_run:
            anchor.suggested_label = suggestion
            anchor.suggested_by = "glossary_keeper"
            anchor.save(update_fields=["suggested_label", "suggested_by"])
            log_keeper_action(
                anchor=anchor,
                assistant=assistant,
                action_taken="suggested_mutation",
                score_before=anchor.avg_score,
                notes=rationale,
            )
            mem = reflect_on_anchor_drift(anchor, rationale, assistant=assistant)
            log_keeper_action(
                anchor=anchor,
                assistant=assistant,
                action_taken="reflection_written",
                notes=mem.summary,
            )
        if auto_promote:
            promote_stable_anchor(anchor)
        processed += 1
    return processed
