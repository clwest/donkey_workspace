import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, TemporalReflectionLog


def test_phase13_6_models_create(db):
    assistant = Assistant.objects.create(name="Alpha", specialty="sage")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    log = TemporalReflectionLog.objects.create(
        assistant=assistant,
        user_id="u1",
        codex_affinity_graph={"a": 1},
        belief_drift_score=0.5,
        timeline_reflection_summary="sum",
    )
    log.memory_snapshots.add(memory)

    assert log.memory_snapshots.count() == 1
    assert log.assistant == assistant
