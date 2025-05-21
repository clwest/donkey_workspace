from __future__ import annotations
from typing import List
from agents.models import (
    LoreToken,
    SwarmMemoryEntry,
    Agent,
    LoreTokenCraftingRitual,
)
from assistants.models import Assistant, AssistantReputation
from embeddings.helpers.helpers_io import get_embedding_for_text
from utils.llm_router import call_llm


def compress_memories_to_token(
    memories: List[SwarmMemoryEntry], created_by: Assistant, token_type: str = "insight"
) -> LoreToken:
    """Summarize memories and package into a LoreToken."""
    text = "\n".join(m.content for m in memories)
    prompt = (
        "Summarize the following assistant memories into a concise mythic lore note:\n"
        + text
    )
    try:
        summary = call_llm(
            [{"role": "user", "content": prompt}],
            model="gpt-4o",
            max_tokens=200,
            temperature=0.3,
        )
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
        token_type=token_type,
        embedding=embedding,
        created_by=created_by,
    )
    if memories:
        token.source_memories.set(memories)
    rep, _ = AssistantReputation.objects.get_or_create(assistant=created_by)
    rep.tokens_created += 1
    rep.reputation_score = (
        rep.tokens_created + rep.tokens_endorsed + rep.tokens_received
    )
    rep.save()
    return token


def perform_token_ritual(ritual: LoreTokenCraftingRitual) -> LoreToken:
    """Finalize a crafting ritual and generate the lore token."""

    token = compress_memories_to_token(
        list(ritual.base_memories.all()),
        ritual.initiating_assistant,
        token_type=ritual.token_type,
    )
    ritual.resulting_token = token
    ritual.completed = True
    ritual.save()
    return token


def apply_lore_token_to_agent(agent: Agent, token: LoreToken) -> None:
    """Update agent skills or beliefs based on the lore token."""
    skills = token.symbolic_tags.get("skills", [])
    if not isinstance(skills, list):
        skills = []
    current = set(agent.skills or [])
    agent.skills = list(current.union(skills))
    agent.save()
