import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    EncodedRitualBlueprint,
    BeliefInheritanceTree,
    RitualResponseArchive,
)


def test_phase12_3_models_create(db):
    assistant = Assistant.objects.create(name="A")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    tree = BeliefInheritanceTree.objects.create(
        user_id="u",
        assistant=assistant,
        core_belief_nodes={"root": 1},
        symbolic_summary="sum",
    )
    tree.memory_links.add(mem)

    archive = RitualResponseArchive.objects.create(
        ritual_blueprint=blueprint,
        assistant=assistant,
        user_id="u",
        ritual_inputs={},
        output_summary="o",
        belief_state_shift={},
    )

    assert tree.memory_links.count() == 1
    assert archive.ritual_blueprint == blueprint
