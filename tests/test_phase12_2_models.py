import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex, EncodedRitualBlueprint
from simulation.models import (
    MythflowPlaybackSession,
    SymbolicMilestoneLog,
    PersonalRitualGuide,
)


def test_phase12_2_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    playback = MythflowPlaybackSession.objects.create(
        user_id="u1",
        assistant=assistant,
        playback_sequence=[{"step": "one"}],
        reflective_summary="sum",
    )

    milestone = SymbolicMilestoneLog.objects.create(
        user_id="u1",
        assistant=assistant,
        milestone_type="ritual_completed",
        codex_context=codex,
        reflection_notes="notes",
    )
    milestone.related_memory.add(mem)

    guide = PersonalRitualGuide.objects.create(
        assistant=assistant,
        user_id="u1",
        ritual_blueprint=blueprint,
        personalized_steps=["step1"],
        codex_alignment_score=0.7,
    )

    assert playback.assistant == assistant
    assert milestone.related_memory.count() == 1
    assert guide.ritual_blueprint == blueprint
