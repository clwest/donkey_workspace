import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    EncodedRitualBlueprint,
    PublicRitualLogEntry,
    BeliefContinuityThread,
    CodexContributionCeremony,
)


def test_phase10_9_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    log = PublicRitualLogEntry.objects.create(
        ritual_title="R",
        participant_identity="user",
        assistant=assistant,
        ritual_blueprint=blueprint,
        reflection_summary="sum",
    )
    log.memory_links.add(mem)

    thread = BeliefContinuityThread.objects.create(
        user_id="u",
        symbolic_tags={"t": 1},
        continuity_score=0.5,
    )
    thread.related_codices.add(codex)
    thread.assistant_interactions.add(assistant)

    ceremony = CodexContributionCeremony.objects.create(
        ceremony_title="T",
        contributor_id="u",
        symbolic_proposal="prop",
        codex_target=codex,
    )

    assert log.memory_links.count() == 1
    assert thread.related_codices.count() == 1
    assert ceremony.codex_target == codex
