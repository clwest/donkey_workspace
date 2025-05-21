from assistants.models import Assistant
from agents.models import LegacyArtifact, ReincarnationLog


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
