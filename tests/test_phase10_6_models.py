import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex, EncodedRitualBlueprint
from simulation.models import (
    MemoryProjectionFrame,
    BeliefNarrativeWalkthrough,
    DreamframePlaybackSegment,
    MythScenarioSimulator,
    MythflowSession,
)


def test_phase10_6_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)
    ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps={})

    sim = MythScenarioSimulator.objects.create(
        simulation_title="s",
        initiating_entity=assistant,
        selected_archetypes={},
        narrative_goals="g",
    )
    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)

    frame = MemoryProjectionFrame.objects.create(
        assistant=assistant,
        symbolic_ritual_overlay=ritual,
        codex_context=codex,
        belief_trigger_tags={"tag": 1},
    )
    frame.projected_memory_sequence.add(mem)

    walk = BeliefNarrativeWalkthrough.objects.create(
        walkthrough_title="W",
        guide_assistant=assistant,
        decision_points=[],
        symbolic_outcome_log="log",
        walkthrough_rating=0.5,
    )

    seg = DreamframePlaybackSegment.objects.create(
        session_context=session,
        playback_source=frame,
        visual_style="basic",
        narration_script="n",
        symbolic_affect_curve={},
    )

    assert frame.projected_memory_sequence.count() == 1
    assert walk.guide_assistant == assistant
    assert seg.playback_source == frame
