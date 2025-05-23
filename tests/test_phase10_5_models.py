import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex
from simulation.models import (
    MythScenarioSimulator,
    MythflowSession,
    BeliefNarrativeEngineInstance,
    SymbolicAuthorityTransferLog,
    MemoryCinematicFragment,
)


def test_phase10_5_models_create(db):
    a1 = Assistant.objects.create(name="A1", specialty="test")
    a2 = Assistant.objects.create(name="A2", specialty="test")
    codex = SwarmCodex.objects.create(title="C", created_by=a1)
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=a1,
        selected_archetypes={"hero": 1},
        narrative_goals="goal",
    )
    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)
    session.participants.add(a1, a2)

    engine = BeliefNarrativeEngineInstance.objects.create(
        engine_name="E",
        driving_codex=codex,
        symbolic_goals={"end": True},
        narrative_trace_log="log",
    )
    engine.assistants_involved.add(a1, a2)

    transfer = SymbolicAuthorityTransferLog.objects.create(
        from_assistant=a1,
        to_assistant=a2,
        scene_context=session,
        symbolic_trigger="t",
        justification="because",
    )

    fragment = MemoryCinematicFragment.objects.create(
        assistant=a1,
        symbolic_filter_tags={"tag": 1},
        cinematic_summary="sum",
        visual_style="noir",
    )
    fragment.memory_sequence.add(mem)

    assert engine.assistants_involved.count() == 2
    assert transfer.scene_context == session
    assert fragment.memory_sequence.count() == 1
