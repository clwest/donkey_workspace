from agents.models.lore import LegacyArtifact, SwarmMemoryEntry
from agents.models.core import Agent


def build_agent_spawn_artifact(agent: Agent, skill: str) -> LegacyArtifact:
    """Create a legacy artifact documenting an agent spawn."""
    memory = SwarmMemoryEntry.objects.create(
        title=f"Agent spawned: {agent.name}",
        content=f"Agent {agent.name} created for skill {skill}",
        origin="spawn",
    )
    artifact = LegacyArtifact.objects.create(
        assistant=agent.parent_assistant,
        artifact_type="agent_spawn",
        source_memory=memory,
        symbolic_tags={"agent_id": str(agent.id), "skill": skill},
    )
    return artifact
