import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    SymbolicResilienceMonitor,
    MythOSDeploymentPacket,
    BeliefDeploymentStrategyEngine,
)


def test_phase16_0_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    monitor = SymbolicResilienceMonitor.objects.create(
        node_id="node1",
        codex_uptime_index=0.9,
        ritual_execution_consistency=0.8,
        memory_integrity_score=0.95,
        symbolic_warning_flags={"w": True},
    )

    packet = MythOSDeploymentPacket.objects.create(
        deployment_name="P",
        deployment_vector="vector",
    )
    packet.bundled_codices.add(codex)
    packet.included_assistants.add(assistant)
    packet.ritual_archive.add(ritual)

    strategy = BeliefDeploymentStrategyEngine.objects.create(
        target_environment="env",
        symbolic_alignment_score=0.8,
        assistant_role_distribution={"A": 1},
        ritual_density_projection={"R": 2},
        codex_coherence_recommendation="Keep myth strong",
    )

    assert monitor.node_id == "node1"
    assert packet.bundled_codices.count() == 1
    assert strategy.target_environment == "env"
