from __future__ import annotations

from typing import Optional
import numpy as np
from django.utils import timezone
from embeddings.vector_utils import compute_similarity
from assistants.models import Assistant, AssistantThoughtLog, SpecializationDriftLog


def analyze_drift_for_assistant(
    assistant: Assistant,
    thought_limit: int = 20,
    threshold: float = 0.8,
) -> Optional[SpecializationDriftLog]:
    """Analyze recent thoughts against the assistant's initial embedding."""
    if assistant.initial_embedding is None:
        return None

    thoughts = (
        AssistantThoughtLog.objects.filter(assistant=assistant, embedding__isnull=False)
        .order_by("-created_at")[:thought_limit]
    )
    if not thoughts:
        return None

    vecs = np.array([t.embedding for t in thoughts])
    avg_vec = vecs.mean(axis=0)
    similarity = compute_similarity(avg_vec.tolist(), assistant.initial_embedding)
    drift_score = 1 - similarity

    assistant.last_drift_check = timezone.now()
    assistant.save(update_fields=["last_drift_check"])

    if similarity < threshold:
        return SpecializationDriftLog.objects.create(
            assistant=assistant, score=drift_score, summary=f"Drift {drift_score:.2f}"
        )
    return None
