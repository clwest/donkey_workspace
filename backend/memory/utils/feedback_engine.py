import logging
from typing import Optional

from prompts.utils.mutation import mutate_prompt as run_mutation
from embeddings.helpers.helpers_io import save_embedding, get_embedding_for_text

from ..models import MemoryFeedback, MemoryEntry
from ..memory_service import get_memory_service

logger = logging.getLogger(__name__)


def apply_memory_feedback(feedback: MemoryFeedback) -> MemoryEntry:
    """Apply a MemoryFeedback suggestion to its memory entry."""
    memory = feedback.memory
    style = feedback.mutation_style or "clarify"
    base_text = memory.summary or memory.event or memory.full_transcript or ""

    try:
        mutated = run_mutation(base_text, style)
    except Exception as exc:  # pragma: no cover - safeguard
        logger.exception("Mutation failed: %s", exc)
        mutated = base_text

    created_entry: Optional[MemoryEntry] = None

    if memory.summary:
        created_entry = MemoryEntry.objects.create(
            assistant=memory.assistant,
            related_project=memory.related_project,
            type="mutation",
            parent_memory=memory,
            triggered_by="memory feedback",
            event=memory.event,
            summary=mutated,
        )
        if memory.tags.exists():
            created_entry.tags.set(memory.tags.all())
        try:
            vector = get_embedding_for_text(mutated)
            if vector:
                save_embedding(created_entry, vector)
                get_memory_service().auto_tag_memory_from_text(created_entry, mutated)
        except Exception:  # pragma: no cover - optional failure
            logger.exception("Embedding failed for mutated memory")
    else:
        memory.summary = mutated
        memory.save(update_fields=["summary"])
        created_entry = memory

    try:
        get_memory_service().log_reflection(feedback.suggestion or mutated, [created_entry])
    except Exception:  # pragma: no cover - safety
        logger.exception("Reflection logging failed")

    return created_entry
