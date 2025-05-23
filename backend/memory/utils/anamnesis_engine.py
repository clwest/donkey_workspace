from assistants.models import Assistant
from agents.models.lore import SwarmMemoryEntry
from memory.models import BraidedMemoryStrand, ContinuityAnchorPoint


def run_anamnesis_retrieval(assistant: Assistant) -> dict:
    """Gather fragmented memories tied to an assistant's myth lineage."""

    strands = BraidedMemoryStrand.objects.filter(primary_assistant=assistant)
    anchors = ContinuityAnchorPoint.objects.filter(assistant=assistant)

    memories = list(
        SwarmMemoryEntry.objects.filter(braided_into__in=strands).distinct()
    )
    memories += [a.anchor_memory for a in anchors]

    titles = [m.title for m in memories]
    summary = "; ".join(titles)
    return {
        "summary": summary,
        "recovery_score": len(memories),
        "symbolic_log": f"Recovered {len(memories)} memory fragments",
    }
