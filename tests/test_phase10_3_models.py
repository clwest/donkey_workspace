import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex
from simulation.models import (
    MythScenarioSimulator,
    MythflowSession,
    SymbolicDialogueScript,
    MemoryDecisionTreeNode,
    SceneControlEngine,
)


def test_phase10_3_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=assistant,
        selected_archetypes={"hero": 1},
        narrative_goals="goal",
    )

    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)

    script = SymbolicDialogueScript.objects.create(
        title="T",
        author=assistant,
        narrative_context="ctx",
        codex_link=codex,
        dialogue_sequence=[{"line": "hi"}],
        archetype_tags=["sage"],
    )

    node = MemoryDecisionTreeNode.objects.create(
        script=script,
        memory_reference=mem,
        symbolic_condition="c",
        decision_options=["a"],
        resulting_path="p",
    )

    scene = SceneControlEngine.objects.create(
        session=session,
        scene_title="Scene",
        active_roles={"hero": assistant.id},
        symbolic_scene_state={},
    )
    scene.codex_constraints.add(codex)

    assert script.author == assistant
    assert node.memory_reference == mem
    assert scene.codex_constraints.count() == 1
