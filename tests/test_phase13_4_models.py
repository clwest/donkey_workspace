import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    SwarmFederationEngine,
    SymbolicProphecyEngine,
    MemoryPredictionInterface,
    RitualForecastingDashboard,
)


def test_phase13_4_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant)
    blueprint = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])
    federation = SwarmFederationEngine.objects.create(
        symbolic_state_map={}, federation_log="", ritual_convergence_score=0.0
    )

    engine = SymbolicProphecyEngine.objects.create(
        engine_name="E",
        assistant_scope=assistant,
        forecast_parameters={"n": 1},
        predicted_codex_shift="shift",
        belief_curve_projection={"v": []},
    )

    mp = MemoryPredictionInterface.objects.create(
        simulated_memory_entry="m",
        codex_context={"c": 1},
        ritual_tags=["r"],
        entropy_score=0.5,
        assistant_belief_response="ok",
        predicted_directive_alignment=0.8,
    )

    dash = RitualForecastingDashboard.objects.create(
        ritual_blueprint=blueprint,
        assistant=assistant,
        codex=codex,
        federation_engine=federation,
        completion_likelihood=0.7,
        symbolic_risk_factor=0.2,
        role_pressure_spikes={"p": 1},
        narrative_alignment_forecast=0.9,
    )

    assert engine.assistant_scope == assistant
    assert mp.entropy_score == 0.5
    assert dash.ritual_blueprint == blueprint
