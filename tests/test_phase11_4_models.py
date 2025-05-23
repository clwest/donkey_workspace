import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    NarrativeLightingEngine,
    CodexVisualElementLayer,
    AssistantAestheticCloneProfile,
)
from simulation.models import MythScenarioSimulator, MythflowSession


def test_phase11_4_models_create(db):
    a1 = Assistant.objects.create(name="A", specialty="t")
    a2 = Assistant.objects.create(name="B", specialty="t")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=a1)
    sim = MythScenarioSimulator.objects.create(
        simulation_title="S",
        initiating_entity=a1,
        selected_archetypes={},
        narrative_goals="g",
    )
    session = MythflowSession.objects.create(session_name="sess", active_scenario=sim)

    engine = NarrativeLightingEngine.objects.create(
        codex=codex,
        mythflow_session=session,
        background_pulse="soft",
        lighting_tint="blue",
    )

    layer = CodexVisualElementLayer.objects.create(
        codex=codex,
        background_tone="dark",
        glyph_overlays={},
        role_frame="oracle",
    )

    clone = AssistantAestheticCloneProfile.objects.create(
        source_assistant=a1,
        target_assistant=a2,
        traits_cloned={},
        symbolic_variants={},
        clone_score=0.7,
    )

    assert engine.codex == codex
    assert layer.codex == codex
    assert clone.target_assistant == a2
