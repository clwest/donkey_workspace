"""Agent-related service functions."""

from django.contrib.contenttypes.models import ContentType

from agents.models import (
    Agent,
    AgentSkill,
    AgentSkillLink,
    AgentLegacy,
    SwarmMemoryEntry,
)
from intel_core.models import Document
from memory.models import MemoryEntry

from .document_service import ingest_documents


def spawn_agent_for_skill(skill: str, base_profile: dict) -> Agent:
    """Create a new specialized agent for the given skill gap."""
    name = base_profile.get("name") or f"{skill.title()} Specialist"
    agent = Agent.objects.create(
        name=name,
        description=base_profile.get("description", ""),
        specialty=skill,
        metadata=base_profile.get("metadata", {}),
        preferred_llm=base_profile.get("preferred_llm", "gpt-4o"),
        execution_mode=base_profile.get("execution_mode", "direct"),
        parent_assistant=base_profile.get("parent_assistant"),
    )

    skill_obj, _ = AgentSkill.objects.get_or_create(name=skill)
    AgentSkillLink.objects.create(agent=agent, skill=skill_obj, source="spawn")

    docs = Document.objects.filter(tags__name__iexact=skill)[:3]
    if docs:
        ingest_documents(docs)

    MemoryEntry.objects.create(
        event=f"Agent {agent.name} spawned with focus on {skill}",
        assistant=agent.parent_assistant,
        source_role="system",
        linked_content_type=ContentType.objects.get_for_model(Agent),
        linked_object_id=agent.id,
    )

    AgentLegacy.objects.get_or_create(agent=agent)

    SwarmMemoryEntry.objects.create(
        title=f"Agent spawned: {agent.name}",
        content=f"Agent {agent.name} created for skill {skill}",
        origin="spawn",
    ).linked_agents.add(agent)

    return agent
