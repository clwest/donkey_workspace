from assistants.models.assistant import Assistant
from agents.models.lore import LegacyArtifact, ReincarnationLog


def reincarnate_assistant_from_artifact(artifact: LegacyArtifact) -> Assistant:
    """Create a new assistant seeded from an artifact's symbolic tags."""
    tags = artifact.symbolic_tags or {}
    name = tags.get("name") or f"{artifact.assistant.name}-reborn"
    assistant = Assistant.objects.create(
        name=name,
        specialty=tags.get("specialty", ""),
        parent_assistant=artifact.assistant,
    )
    log = ReincarnationLog.objects.create(
        ancestor=artifact.assistant,
        descendant=assistant,
        reincarnation_reason="from_artifact",
    )
    log.inherited_artifacts.add(artifact)
    return assistant


def initiate_reincarnation_flow(assistant_id: int) -> dict:
    """Propose a rebirth blueprint using the assistant's current context."""

    assistant = Assistant.objects.get(id=assistant_id)
    blueprint = {
        "name": f"{assistant.name}-rebirth",
        "legacy_traits": assistant.traits,
        "preferred_model": assistant.preferred_model,
    }
    return {"assistant": assistant_id, "blueprint": blueprint}
