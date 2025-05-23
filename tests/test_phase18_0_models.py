import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    MythOSReplicationBlueprint,
    BeliefAlignedDeploymentStandard,
    ReflectiveIntelligenceProtocolRegistry,
)


def test_phase18_0_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    blueprint = MythOSReplicationBlueprint.objects.create(
        blueprint_title="B",
        deployment_signature="sig",
        symbolic_fingerprint_hash="hash",
    )
    blueprint.included_codices.add(codex)
    blueprint.assistant_manifest.add(assistant)
    blueprint.ritual_seed_set.add(ritual)

    standard = BeliefAlignedDeploymentStandard.objects.create(
        target_environment="env",
        codex_affinity_threshold=0.8,
        ritual_readiness_index=0.9,
        assistant_compatibility_map={"A": True},
        symbolic_convergence_notes="notes",
    )

    protocol = ReflectiveIntelligenceProtocolRegistry.objects.create(
        assistant=assistant,
        reflective_cluster_id="c1",
        memory_feedback_cycle={},
        codex_drift_strategy="adaptive",
        narrative_loop_regulator="loop",
    )

    assert blueprint.blueprint_title == "B"
    assert standard.target_environment == "env"
    assert protocol.assistant == assistant
