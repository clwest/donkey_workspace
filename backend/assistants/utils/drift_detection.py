from __future__ import annotations

import logging
import numpy as np
from typing import Optional
from django.db.models import QuerySet
from django.utils import timezone

from assistants.models.assistant import Assistant, SpecializationDriftLog
from assistants.models.assistant import ChatIntentDriftLog
from memory.models import SymbolicMemoryAnchor
from assistants.models.thoughts import AssistantThoughtLog
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger(__name__)

THOUGHT_SAMPLE_SIZE = 20
SIMILARITY_THRESHOLD = 0.8


def _get_baseline_embedding(assistant: Assistant) -> list[float] | None:
    if assistant.embedding:
        return list(assistant.embedding)
    if assistant.system_prompt and assistant.system_prompt.embedding:
        return list(assistant.system_prompt.embedding)
    return None


def analyze_specialization_drift(assistant: Assistant) -> dict:
    """Return drift analysis details for an assistant."""
    baseline = _get_baseline_embedding(assistant)
    if not baseline:
        return {
            "drift_score": 0.0,
            "flagged": False,
            "summary": "No baseline embedding available",
        }

    if assistant.system_prompt and assistant.system_prompt.content:
        current_embedding = get_embedding_for_text(assistant.system_prompt.content)
    else:
        current_embedding = baseline

    prompt_sim = compute_similarity(current_embedding, baseline)

    logs: QuerySet[AssistantThoughtLog] = (
        AssistantThoughtLog.objects.filter(assistant=assistant)
        .exclude(thought="")
        .order_by("-created_at")[:THOUGHT_SAMPLE_SIZE]
    )
    scores = []
    for t in logs:
        emb = list(t.embedding) if t.embedding else get_embedding_for_text(t.thought)
        scores.append(compute_similarity(emb, baseline))

    avg_thought_sim = sum(scores) / len(scores) if scores else prompt_sim
    overall_sim = (prompt_sim + avg_thought_sim) / 2

    flagged = overall_sim < SIMILARITY_THRESHOLD
    if flagged:
        assistant.needs_recovery = True
        assistant.save(update_fields=["needs_recovery"])

    return {
        "drift_score": 1 - overall_sim,
        "prompt_similarity": prompt_sim,
        "thought_similarity": avg_thought_sim,
        "flagged": flagged,
        "requires_retraining": flagged,
        "summary": f"Similarity to baseline {overall_sim:.2f}",
    }


def analyze_drift_for_assistant(
    assistant: Assistant,
    thought_limit: int = THOUGHT_SAMPLE_SIZE,
    threshold: float = SIMILARITY_THRESHOLD,
) -> Optional[SpecializationDriftLog]:
    """Lightweight drift checker that logs to DB if drift exceeds threshold."""
    if assistant.embedding is None:
        return None

    thoughts = (
        AssistantThoughtLog.objects.filter(assistant=assistant, embedding__isnull=False)
        .order_by("-created_at")[:thought_limit]
    )
    if not thoughts:
        return None

    vecs = np.array([t.embedding for t in thoughts])
    avg_vec = vecs.mean(axis=0)
    similarity = compute_similarity(avg_vec.tolist(), assistant.embedding)
    drift_score = 1 - similarity

    assistant.last_drift_check = timezone.now()
    assistant.save(update_fields=["last_drift_check"])

    if similarity < threshold:
        return SpecializationDriftLog.objects.create(
            assistant=assistant,
            drift_score=drift_score,
            summary=f"Drift {drift_score:.2f}",
            trigger_type="auto",
            auto_flagged=True,
        )

    return None


def detect_drift_or_miss(message: str, assistant: Assistant) -> tuple[float, list[str]]:
    """Return drift score and matched anchor slugs for a user message."""
    if not message:
        return 0.0, []

    anchors = list(SymbolicMemoryAnchor.objects.values_list("slug", flat=True))
    matched = [a for a in anchors if a.lower() in message.lower()]

    objective_terms = []
    for obj in assistant.objectives.all():
        objective_terms.extend(obj.title.lower().split())

    all_terms = set(anchors + objective_terms)
    hits = [t for t in all_terms if t.lower() in message.lower()]
    drift_score = 1.0 - len(hits) / len(all_terms) if all_terms else 0.0
    return drift_score, matched
