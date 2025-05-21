import logging
from typing import Dict

from assistants.models import Assistant, ConscienceModule

logger = logging.getLogger(__name__)


def run_reflexive_belief_audit(assistant: Assistant) -> Dict:
    """Evaluate alignment between conscience values and belief vector."""

    conscience = getattr(assistant, "conscience", None)
    belief = assistant.belief_vector or {}

    if not conscience:
        logger.warning("Assistant %s has no conscience module", assistant.id)
        return {"score": 0.0, "issues": ["no_conscience"]}

    core_values = set(conscience.core_values or [])
    belief_values = set(belief.get("values") or [])
    alignment = len(core_values & belief_values) / (len(core_values) or 1)

    contradictions = [v for v in belief_values if v not in core_values]

    return {
        "alignment_score": round(alignment, 2),
        "contradictions": contradictions,
    }
