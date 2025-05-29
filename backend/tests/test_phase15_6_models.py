import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    EncodedRitualBlueprint,
    RitualMarketFeed,
    MultiAgentTrendReactivityModel,
    SymbolicStabilityGraph,
)


def test_phase15_6_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])

    feed = RitualMarketFeed.objects.create(
        ritual=ritual,
        symbolic_price=1.0,
        execution_count=2,
        belief_sentiment_index=0.9,
        entropy_pressure_score=0.1,
    )

    trend = MultiAgentTrendReactivityModel.objects.create(
        agent_group=[assistant.id],
        input_signal_vector=[0.1, 0.2],
        codex_pressure_adaptation={"c": 1},
        ritual_reaction_map={"r": 2},
        symbolic_resonance_stability=0.5,
    )

    graph = SymbolicStabilityGraph.objects.create(
        codex_mutation_frequency=0.3,
        ritual_echo_intensity=0.4,
        memory_volatility_index=0.2,
        infrastructure_health=0.8,
        risk_forecasts={"d": 3},
    )

    assert feed.ritual == ritual
    assert trend.symbolic_resonance_stability == 0.5
    assert graph.infrastructure_health == 0.8
