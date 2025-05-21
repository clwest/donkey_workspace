from typing import Dict
from uuid import UUID
from django.utils import timezone
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread
from agents.models import SwarmMemoryEntry, Agent
from .thread_helpers import recall_from_thread
from utils.llm import call_gpt4


def compress_memory_thread(thread_id: UUID) -> Dict:
    """Summarize and compress a memory thread for archival."""
    try:
        thread = NarrativeThread.objects.get(id=thread_id)
    except NarrativeThread.DoesNotExist:
        return {}

    memories = list(
        MemoryEntry.objects.filter(thread_id=thread_id).order_by("created_at")[:40]
    )
    if not memories:
        return {}

    text = "\n".join(m.summary or m.event for m in memories)
    prompt = (
        "Summarize the following memory thread in concise bullet points. "
        "Highlight key agents and themes.\n\n" + text
    )
    summary = call_gpt4(prompt, model="gpt-4o-mini", max_tokens=400)

    agents = Agent.objects.filter(memory_entries__in=memories).distinct()
    tags = sorted({t.slug for m in memories for t in m.tags.all()})

    entry = SwarmMemoryEntry.objects.create(
        title=f"Compressed Thread: {thread.title}",
        content=summary,
        origin="compression",
    )
    if agents:
        entry.linked_agents.set(agents)

    return {
        "summary": summary,
        "key_agents": [
            {"id": str(a.id), "name": a.name} for a in agents
        ],
        "tags": tags,
        "compressed": summary,
    }
