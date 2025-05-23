import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    EncodedRitualBlueprint,
    BeliefInheritanceTree,
    RitualResponseArchive,
)
from agents.utils.journey_export import create_myth_journey_package
import tempfile
import os


def test_phase12_3_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="oracle")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    tree = BeliefInheritanceTree.objects.create(
        user_id="u1",
        assistant=assistant,
        core_belief_nodes={"root": "a"},
        symbolic_summary="sum",
    )
    tree.memory_links.add(mem)

    archive = RitualResponseArchive.objects.create(
        ritual_blueprint=blueprint,
        assistant=assistant,
        user_id="u1",
        ritual_inputs={"q": 1},
        output_summary="out",
        belief_state_shift={"s": 2},
    )

    assert tree.memory_links.count() == 1
    assert archive.assistant == assistant

    with tempfile.TemporaryDirectory() as tmpdir:
        path = create_myth_journey_package("u1", assistant, tmpdir, memories=[mem])
        assert os.path.exists(path)

