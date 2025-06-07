import logging
from typing import Optional, Tuple

from django.utils import timezone

from utils.llm import call_gpt4
from mcp_core.models import Tag
from memory.models import (
    SymbolicMemoryAnchor,
    MemoryEntry,
    GlossaryKeeperLog,
)
from .reflection_replay import replay_reflection

logger = logging.getLogger(__name__)

DRIFT_THRESHOLD = 0.5


def calculate_anchor_drift(anchor: SymbolicMemoryAnchor) -> float:
    """Return fraction of anchor chunks marked as drifting."""
    total = anchor.chunks.count()
    drifting = anchor.chunks.filter(is_drifting=True).count()
    return round(drifting / total, 2) if total else 0.0


def suggest_mutation_with_rationale(anchor: SymbolicMemoryAnchor) -> Tuple[str, str]:
    """Ask GPT for a clearer term and rationale."""
    prompt = (
        f'The glossary term "{anchor.label}" is drifting in usage. '
        "Suggest a clearer replacement term and briefly explain why."
    )
    try:
        response = call_gpt4(prompt)
    except Exception as exc:  # pragma: no cover - network issues
        logger.exception("GPT error: %s", exc)
        return "", ""
    parts = response.split("\n", 1)
    label = parts[0].strip().strip('"').strip(".")
    rationale = parts[1].strip() if len(parts) > 1 else ""
    return label, rationale


def log_keeper_action(
    anchor: SymbolicMemoryAnchor,
    assistant,
    action_taken: str,
    score_before: float,
    score_after: float,
    notes: str = "",
) -> None:
    GlossaryKeeperLog.objects.create(
        anchor=anchor,
        assistant=assistant,
        action_taken=action_taken,
        score_before=score_before,
        score_after=score_after,
        notes=notes,
    )


def run_keeper_tasks(assistant=None) -> None:
    """Run glossary drift checks and record actions."""
    anchors = SymbolicMemoryAnchor.objects.all()
    if assistant:
        anchors = anchors.filter(assistant=assistant)
    drift_tag, _ = Tag.objects.get_or_create(
        slug="glossary_drift", defaults={"name": "glossary_drift"}
    )
    for anchor in anchors:
        drift = calculate_anchor_drift(anchor)
        if drift < DRIFT_THRESHOLD:
            continue
        score_before = anchor.avg_score
        notes = ""
        action = "reviewed"
        if not anchor.suggested_label:
            suggestion, notes = suggest_mutation_with_rationale(anchor)
            if suggestion:
                anchor.suggested_label = suggestion
                anchor.mutation_source = "keeper"
                anchor.save(update_fields=["suggested_label", "mutation_source"])
                action = "suggested_mutation"
        summary = (
            f"The term {anchor.label} has shown increasing drift. Suggested fix: "
            f"{anchor.suggested_label or ''}."
        )
        mem = MemoryEntry.objects.create(
            assistant=anchor.assistant or assistant,
            anchor=anchor,
            summary=summary,
            event=summary,
            context=anchor.memory_context,
            type="reflection",
            source_role="system",
        )
        mem.tags.add(drift_tag)
        # optional: replay reflection if drift worsens
        if action == "suggested_mutation" and drift > DRIFT_THRESHOLD:
            try:
                replay_reflection(mem)
            except Exception as exc:  # pragma: no cover - runtime safeguard
                logger.exception("Replay failed: %s", exc)
        log_keeper_action(
            anchor,
            assistant or anchor.assistant,
            action,
            score_before,
            anchor.avg_score,
            notes,
        )

