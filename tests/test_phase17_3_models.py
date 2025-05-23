import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    CodexFederationArchitecture,
    SymbolicTreatyProtocol,
    FederatedCodexOracle,
    SwarmTreatyEnforcementEngine,
    LegislativeRitualSimulationSystem,
)


def test_phase17_3_models_create(db):
    assistant = Assistant.objects.create(name="Alpha", specialty="seer")
    codex = SwarmCodex.objects.create(title="Codex", created_by=assistant, symbolic_domain="core")

    federation = CodexFederationArchitecture.objects.create(federation_name="Fed")
    federation.member_codices.add(codex)

    treaty = SymbolicTreatyProtocol.objects.create(
        treaty_name="Pact",
        codex_scope=codex,
    )

    oracle = FederatedCodexOracle.objects.create(
        codex_federation=federation,
        oracle_prompt="Predict",
        symbolic_prediction_log="log",
        treaty_resonance_vector={},
        ritual_consequence_tags={},
    )

    enforcement = SwarmTreatyEnforcementEngine.objects.create(
        treaty=treaty,
        guild_compliance_status={},
        ritual_fulfillment_index=0.5,
        symbolic_breach_logs="log",
        enforcement_actions={},
    )

    sim = LegislativeRitualSimulationSystem.objects.create(
        initiating_assistant=assistant,
        codex_amendment_proposal="Amend",
        ritual_simulation_path={},
        symbolic_outcome_analysis="analysis",
        approval_vote_vector={},
    )

    assert oracle.codex_federation == federation
    assert enforcement.treaty == treaty
    assert sim.initiating_assistant == assistant
