import logging
from typing import List, Dict

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry

logger = logging.getLogger(__name__)


def reason_with_belief(assistant: Assistant, context: str) -> str:
    """Return a reflection influenced by the assistant's belief vector."""

    belief = assistant.belief_vector or {}
    tone = belief.get("tone") or assistant.tone or "neutral"
    values = belief.get("values") or assistant.values

    logger.debug("Belief reasoning", extra={"assistant": assistant.id})

    parts = [f"Tone: {tone}"]
    if values:
        parts.append("Values: " + ", ".join(map(str, values)))
    parts.append(context)
    reflection = " | ".join(parts)

    SwarmMemoryEntry.objects.create(
        title=f"Belief reasoning for {assistant.name}",
        content=reflection,
    )
    return reflection


def align_mythic_memory(assistant: Assistant, conflicting_entries: List[Dict]) -> Dict:
    """Resolve conflicting mythic memories and log the outcome."""

    if not conflicting_entries:
        return {"action": "none", "result": []}

    merged_text = "\n".join(e.get("content") or "" for e in conflicting_entries)
    result = {
        "action": "merge",
        "result": merged_text,
    }

    SwarmMemoryEntry.objects.create(
        title=f"Mythic memory alignment for {assistant.name}",
        content=merged_text,
    )
    return result
