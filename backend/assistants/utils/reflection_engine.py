import logging
from django.utils.text import slugify
from utils.llm_router import call_llm
from memory.models import MemoryEntry
from mcp_core.models import Tag

logger = logging.getLogger(__name__)


def log_symbolic_reflection(
    assistant,
    clause_before: str,
    clause_after: str,
    symbolic_gain: float,
    campaign_id,
):
    """Generates and logs a reflection for an assistant about a codex clause update."""
    prompt = (
        f"You are {assistant.name}, reflecting on an updated codex clause.\n\n"
        f"Clause before:\n{clause_before}\n\n"
        f"Clause after:\n{clause_after}\n\n"
        "How does this change affect your behavior or beliefs? "
        "Respond in 3-5 concise bullet points."
    )

    try:
        reflection = call_llm(
            [{"role": "user", "content": prompt}],
            model=getattr(assistant, "preferred_model", "gpt-4o"),
            max_tokens=300,
        )
    except Exception as exc:  # pragma: no cover - log and fallback
        logger.error("symbolic reflection failed: %s", exc)
        reflection = "Reflection generation failed."

    entry = MemoryEntry.objects.create(
        event=reflection,
        assistant=assistant,
        source_role="assistant",
        symbolic_change=True,
        related_campaign_id=campaign_id,
        type="codex_reflection",
    )

    for label in ["symbolic_change", "codex_update"]:
        tag, _ = Tag.objects.get_or_create(slug=slugify(label), defaults={"name": label})
        entry.tags.add(tag)

    return entry
