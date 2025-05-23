import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, RitualBlueprint
from simulation.models import (
    MythScenarioSimulator,
    RitualInteractionEvent,
    SimulationStateTracker,
)


def test_phase10_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    blueprint = RitualBlueprint.objects.create(name="B", steps=["s"])

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=assistant,
        selected_archetypes={"hero": 1},
        narrative_goals="goal",
    )
    sim.memory_inputs.add(mem)

    event = RitualInteractionEvent.objects.create(
        assistant=assistant,
        ritual_blueprint=blueprint,
        trigger_method="button",
        belief_impact_score=0.5,
    )
    event.memory_write_back = mem
    event.save()

    tracker = SimulationStateTracker.objects.create(
        simulator=sim,
        symbolic_state_snapshot={"phase": 1},
        codex_alignment_score=0.9,
        memory_deltas={"m": 1},
    )

    assert sim.memory_inputs.count() == 1
    assert event.memory_write_back == mem
    assert tracker.codex_alignment_score == 0.9
