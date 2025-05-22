from __future__ import annotations
import logging
from typing import List, Tuple
from django.contrib.contenttypes.models import ContentType

from assistants.models.assistant import Assistant
from memory.models import MemoryEntry
from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.models import Embedding
from embeddings.vector_utils import compute_similarity

logger = logging.getLogger(__name__)


def search_related_memories(
    text: str, assistant: Assistant, top_n: int = 5
) -> List[MemoryEntry]:
    """Return top-N memories from this assistant most similar to the text."""
    try:
        query_vec = get_embedding_for_text(text)
    except Exception as e:  # pragma: no cover - network failure
        logger.warning("Embedding generation failed: %s", e)
        return []

    if not query_vec:
        return []

    ct = ContentType.objects.get_for_model(MemoryEntry)
    mem_ids = list(
        MemoryEntry.objects.filter(assistant=assistant).values_list("id", flat=True)
    )
    if not mem_ids:
        return []

    embeddings = Embedding.objects.filter(content_type=ct, object_id__in=mem_ids)
    scored: List[Tuple[float, MemoryEntry]] = []
    mem_map = {m.id: m for m in MemoryEntry.objects.filter(id__in=mem_ids)}
    for emb in embeddings:
        mem = mem_map.get(emb.object_id)
        if not mem:
            continue
        score = compute_similarity(query_vec, emb.embedding)
        scored.append((score, mem))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:top_n]]


def summon_relevant_memories(
    text: str, assistant: Assistant, limit: int = 3
) -> Tuple[str, List[str]]:
    """Build a recall block of relevant memories."""
    memories = search_related_memories(text, assistant, top_n=limit)
    if not memories:
        return "", []
    lines = ["# Recalled Memories:"]
    ids = []
    for mem in memories:
        summary = mem.summary or mem.event[:100]
        lines.append(summary)
        ids.append(str(mem.id))
    return "\n".join(lines), ids
