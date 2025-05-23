import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SymbolicIdentityCard,
    PersonaFusionEvent,
    SwarmCodex,
    DialogueCodexMutationLog,
)
from simulation.models import MythScenarioSimulator, MythflowSession, SceneDirectorFrame


def test_phase10_4_models_create(db):
    a1 = Assistant.objects.create(name="A")
    a2 = Assistant.objects.create(name="B")
    card = SymbolicIdentityCard.objects.create(
        assistant=a1,
        archetype="hero",
        symbolic_tags={},
        myth_path="path",
        purpose_signature="sig",
    )
    fusion = PersonaFusionEvent.objects.create(
        initiating_assistant=a1,
        fused_with=a2,
        resulting_identity_card=card,
        memory_alignment_summary="sum",
        fusion_archetype="hero-bard",
    )

    codex = SwarmCodex.objects.create(title="C", created_by=a1, symbolic_domain="test")
    mutation = DialogueCodexMutationLog.objects.create(
        codex=codex,
        triggering_dialogue="hi",
        mutation_reason="update",
        symbolic_impact={"rule": "new"},
    )
    mutation.approved_by.add(a1)

    sim = MythScenarioSimulator.objects.create(
        simulation_title="title",
        initiating_entity=a1,
        selected_archetypes={},
        narrative_goals="goal",
    )
    session = MythflowSession.objects.create(session_name="S", active_scenario=sim)
    frame = SceneDirectorFrame.objects.create(
        session=session,
        director_assistant=a1,
        symbolic_adjustments={},
        role_reassignments={},
        final_scene_notes="done",
    )

    assert fusion.fusion_archetype == "hero-bard"
    assert mutation.codex == codex
    assert frame.session == session
