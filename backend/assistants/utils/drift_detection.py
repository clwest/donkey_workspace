from __future__ import annotations

import logging
from django.db.models import QuerySet
from assistants.models import Assistant, AssistantThoughtLog
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

    result = {
        "drift_score": 1 - overall_sim,
        "prompt_similarity": prompt_sim,
        "thought_similarity": avg_thought_sim,
        "flagged": overall_sim < SIMILARITY_THRESHOLD,
        "summary": f"Similarity to baseline {overall_sim:.2f}",
    }
    return result
