import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmCodex, SymbolicForecastIndex, AssistantSentimentModelEngine


def test_phase15_5_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")

    forecast = SymbolicForecastIndex.objects.create(
        index_title="F",
        linked_codex=codex,
        trend_components={"c": 1},
        ritual_activity_factor=0.5,
        memory_entropy_factor=0.3,
        forecast_output={"f": 2},
    )

    sentiment = AssistantSentimentModelEngine.objects.create(
        assistant=assistant,
        symbolic_affect_log={"a": 1},
        codex_resonance_score=0.7,
        entropy_weighted_emotion_vector=[0.1, 0.2],
        narrative_drift_tag="stable",
    )

    assert forecast.linked_codex == codex
    assert sentiment.assistant == assistant
