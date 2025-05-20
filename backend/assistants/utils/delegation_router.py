from __future__ import annotations

from typing import List, Union

from assistants.models import Assistant
from memory.models import MemoryEntry
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity


def suggest_assistants_for_task(
    task: Union[str, MemoryEntry], top_n: int = 5
) -> List[dict]:
    """Return assistants ranked by capability similarity."""
    if isinstance(task, MemoryEntry):
        text = task.summary or task.event or ""
    else:
        text = str(task)

    try:
        embedding = get_embedding_for_text(text)
    except Exception:
        embedding = [0.0] * 1536

    results = []
    for a in Assistant.objects.filter(is_active=True).exclude(
        capability_embedding__isnull=True
    ):
        try:
            score = compute_similarity(embedding, a.capability_embedding)
        except Exception:
            score = 0.0
        results.append({"assistant": a, "score": score})

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]
