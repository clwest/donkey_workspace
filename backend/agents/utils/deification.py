from django.db.models import Avg

from agents.models import (
    SwarmMemoryEntry,
    DeifiedSwarmEntity,
    MemoryDialect,
    TranscendentMyth,
)
from assistants.models import AssistantCivilization


def evaluate_deification_potential() -> dict:
    """Evaluate swarm metrics and create a deified entity if threshold met."""

    coherence = SwarmMemoryEntry.objects.count()
    convergence = (
        MemoryDialect.objects.aggregate(avg=Avg("alignment_curve")).get("avg") or 1.0
    )
    prophecy_fulfillment = 0.0  # placeholder for future tracking

    score = (coherence * convergence) / 10.0
    result = {
        "canon_coherence": coherence,
        "symbolic_convergence": convergence,
        "prophecy_fulfillment": prophecy_fulfillment,
        "score": round(score, 2),
    }

    if score >= 1.0:
        myth, _ = TranscendentMyth.objects.get_or_create(name="Swarm Genesis")
        mem = SwarmMemoryEntry.objects.order_by("id").first()
        entity = DeifiedSwarmEntity.objects.create(
            name="The Unified Swarm",
            dominant_myth=myth,
            established_through=mem,
            worship_traits={"score": result["score"]},
        )
        civ = AssistantCivilization.objects.first()
        if civ:
            entity.origin_civilizations.add(civ)
        result["deified_entity"] = entity.id
    return result
