from __future__ import annotations
from typing import List
from agents.models import LoreToken, SwarmMemoryEntry, Agent
from assistants.models import Assistant
from embeddings.helpers.helpers_io import get_embedding_for_text
from utils.llm_router import call_llm


def compress_memories_to_token(memories: List[SwarmMemoryEntry], created_by: Assistant) -> LoreToken:
    """Summarize memories and package into a LoreToken."""
    text = "\n".join(m.content for m in memories)
    prompt = (
        "Summarize the following assistant memories into a concise mythic lore note:\n"
        + text
    )
    try:
        summary = call_llm([{"role": "user", "content": prompt}], model="gpt-4o", max_tokens=200, temperature=0.3)
    except Exception:
        summary = text[:200]
    try:
        embedding = get_embedding_for_text(summary)
    except Exception:
        embedding = [0.0] * 1536
    tags = sorted({t.slug for m in memories for t in m.tags.all()})
    token = LoreToken.objects.create(
        name=summary[:150],
        summary=summary,
        symbolic_tags={"tags": tags},
        embedding=embedding,
        created_by=created_by,
    )
    if memories:
        token.source_memories.set(memories)
    return token


def apply_lore_token_to_agent(agent: Agent, token: LoreToken) -> None:
    """Update agent skills or beliefs based on the lore token."""
    skills = token.symbolic_tags.get("skills", [])
    if not isinstance(skills, list):
        skills = []
    current = set(agent.skills or [])
    agent.skills = list(current.union(skills))
    agent.save()
