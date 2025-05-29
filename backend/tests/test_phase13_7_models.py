import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmCodex
from simulation.models import (
    DreamframeStoryGenerator,
    SimScenarioEngine,
    MultiUserNarrativeLab,
)


def test_phase13_7_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="sage")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")

    generator = DreamframeStoryGenerator.objects.create(
        assistant=assistant,
        seed_codex=codex,
        ritual_resonance_tags=["tag"],
        output_script="script",
        symbolic_style="style",
    )

    engine = SimScenarioEngine.objects.create(
        scenario_title="Sim",
        host_assistant=assistant,
        symbolic_inputs={"x": 1},
        user_paths={"path": []},
        codex_alterations={"a": 1},
        ritual_outcomes={"o": 1},
    )

    lab = MultiUserNarrativeLab.objects.create(
        lab_title="Lab",
        participant_ids=["u1"],
        narrative_threads={"t": 1},
        symbolic_experiments={"e": 1},
    )
    lab.assistant_mediators.add(assistant)

    assert generator.assistant == assistant
    assert engine.host_assistant == assistant
    assert lab.assistant_mediators.count() == 1

