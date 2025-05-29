import logging
from typing import Dict

from assistants.models.assistant import Assistant
from embeddings.helpers.helpers_io import get_embedding_for_text
from memory.models import SymbolicMemoryAnchor

logger = logging.getLogger(__name__)


def generate_rag_profile_from_reflection(assistant: Assistant) -> Dict[str, object]:
    """Generate and store a RAG preference vector and anchor weight profile."""
    parts = []
    if assistant.archetype:
        parts.append(assistant.archetype)
    if assistant.dream_symbol:
        parts.append(assistant.dream_symbol)
    if assistant.init_reflection:
        parts.append(assistant.init_reflection)
    text = " ".join(parts).strip()
    if not text:
        return {"updated": False, "reason": "no_text"}

    try:
        vec = get_embedding_for_text(text)
    except Exception as exc:  # pragma: no cover - network issues
        logger.error("Failed to embed rag profile text: %s", exc)
        return {"updated": False, "reason": "embedding_error"}

    assistant.preferred_rag_vector = vec

    lower_text = text.lower()
    weights: Dict[str, float] = {}
    for anchor in SymbolicMemoryAnchor.objects.all():
        weight = 0.0
        if anchor.slug.lower() in lower_text or anchor.label.lower() in lower_text:
            weight = 0.8
        elif any(tag.slug in lower_text for tag in anchor.tags.all()):
            weight = 0.6
        if weight:
            weights[anchor.slug] = weight

    assistant.anchor_weight_profile = weights
    assistant.save(update_fields=["preferred_rag_vector", "anchor_weight_profile"])
    return {"updated": True, "weights": weights}
