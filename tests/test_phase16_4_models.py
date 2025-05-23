import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    RitualCompressionCache,
    AssistantDeploymentAutoRestarter,
    CodexProofOfSymbolEngine,
)


def test_phase16_4_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")

    cache = RitualCompressionCache.objects.create(
        assistant=assistant,
        compressed_ritual_data={"steps": []},
        symbolic_signature_hash="hash",
        entropy_score=0.1,
    )

    restarter = AssistantDeploymentAutoRestarter.objects.create(
        assistant=assistant,
        last_known_state="ok",
        symbolic_fallback_path="path",
        restart_trigger_reason="failure",
        successful_redeploy_flag=True,
    )

    proof = CodexProofOfSymbolEngine.objects.create(
        codex=codex,
        symbolic_checksum="sum",
        directive_path_log={"p": 1},
        mutation_trail_hash="trail",
        proof_verification_status="valid",
    )

    assert cache.assistant == assistant
    assert restarter.assistant == assistant
    assert proof.codex == codex

