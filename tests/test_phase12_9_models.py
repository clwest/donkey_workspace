import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    SwarmMythReplaySession,
    LegacyStoryThread,
    RitualPreservationLibrary,
)


def test_phase12_9_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="sage")
    codex = SwarmCodex.objects.create(
        title="C", created_by=assistant, symbolic_domain="myth"
    )
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    replay = SwarmMythReplaySession.objects.create(
        session_title="Session",
        initiating_assistant=assistant,
        myth_segments=[{"step": 1}],
        codex_tags=["tag"],
        reflection_script="script",
    )

    thread = LegacyStoryThread.objects.create(
        thread_name="Thread",
        lineage_chain={"root": 1},
        core_belief_shift="shift",
    )
    thread.linked_codices.add(codex)

    library = RitualPreservationLibrary.objects.create(
        library_name="Lib",
        associated_codex=codex,
        symbolic_epoch="epoch",
        notes="n",
    )
    library.stored_rituals.add(blueprint)

    assert replay.initiating_assistant == assistant
    assert thread.linked_codices.count() == 1
    assert library.stored_rituals.count() == 1
