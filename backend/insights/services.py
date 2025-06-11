from difflib import SequenceMatcher
from agents.models import Agent
from intel_core.models import Document
from memory.models import MemoryEntry
from .models import SymbolicAgentInsightLog


def detect_document_conflicts(assistant, document: Document) -> None:
    """Check for symbolic conflicts between document and assistant memory."""
    agent: Agent | None = assistant.assigned_agents.first()
    if not agent:
        return
    content_lower = (document.content or "").lower()
    memories = (
        MemoryEntry.objects.filter(assistant=assistant, anchor__isnull=False)
        .select_related("anchor")
        .exclude(summary__isnull=True)
    )
    for mem in memories:
        ratio = SequenceMatcher(None, mem.summary.lower(), content_lower).ratio()
        if ratio < 0.3 and mem.anchor:
            SymbolicAgentInsightLog.objects.create(
                agent=agent,
                document=document,
                symbol=mem.anchor.slug,
                conflict_score=round(1.0 - ratio, 2),
                resolution_method="pending",
                notes=f"Auto-detected conflict with memory {mem.id}",
            )
