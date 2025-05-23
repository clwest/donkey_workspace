import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry
from simulation.models import MythScenarioSimulator, MythflowSession, MythflowReflectionLoop
from simulation.utils import calculate_narrative_pressure
from agents.models import AgentPlotlineCuration


def test_phase10_2_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=assistant,
        selected_archetypes={"hero": 1},
        narrative_goals="goal",
    )

    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)
    session.participants.add(assistant)
    session.memory_trace.add(mem)

    loop = MythflowReflectionLoop.objects.create(
        session=session,
        triggered_by="entropy",
        loop_reflections="test",
        belief_realignment_score=0.5,
    )
    loop.involved_assistants.add(assistant)

    pressure = calculate_narrative_pressure(session.id)

    curation = AgentPlotlineCuration.objects.create(
        assistant=assistant,
        curated_arc_title="Arc",
        narrative_branch_notes="notes",
        symbolic_convergence_score=0.7,
    )
    curation.associated_memories.add(mem)

    assert loop in MythflowReflectionLoop.objects.all()
    assert pressure["entropy"] == 1
    assert curation.associated_memories.count() == 1
