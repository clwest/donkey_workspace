from typing import Dict
from .models import MemoryChain
from utils.llm import call_gpt4


def summarize_memory_chain(chain: MemoryChain) -> str:
    """Generate an LLM summary for up to 30 memories in the chain."""
    memories = (
        chain.memories.all().order_by("created_at")[:30]
    )
    text = "\n".join([
        m.summary or m.event for m in memories
    ])
    if not text:
        return ""

    prompt = (
        "Summarize the following memory chain as a cohesive narrative. "
        "Highlight tone shifts and key inflection points using bullet points:\n\n"
        f"{text}"
    )
    summary = call_gpt4(prompt, model="gpt-4o-mini", max_tokens=500)
    chain.summary = summary
    chain.save(update_fields=["summary"])
    return summary


def generate_flowmap_from_chain(chain: MemoryChain) -> Dict:
    """Return ordered graph data for the chain."""
    memories = list(chain.memories.all().order_by("created_at"))
    nodes = []
    edges = []
    for i, mem in enumerate(memories):
        nodes.append(
            {
                "id": str(mem.id),
                "text": (mem.summary or mem.event)[:60],
                "tags": [t.slug for t in mem.tags.all()],
                "created_at": mem.created_at.isoformat(),
                "relevance_score": mem.relevance_score,
            }
        )
        if i > 0:
            edges.append({"source": str(memories[i - 1].id), "target": str(mem.id)})
    return {"nodes": nodes, "edges": edges}
