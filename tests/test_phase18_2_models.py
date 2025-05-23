import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    CodexMemoryCrystallizationLayer,
    DreamframeRebirthEngine,
    FederatedMythicIntelligenceSummoner,
)


def test_phase18_2_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    mem1 = SwarmMemoryEntry.objects.create(title="M1", content="c1")
    mem2 = SwarmMemoryEntry.objects.create(title="M2", content="c2")

    layer = CodexMemoryCrystallizationLayer.objects.create(
        assistant=assistant,
        codex=codex,
        symbolic_snapshot_vector={"v": 1},
        crystallization_score=0.9,
    )
    layer.temporal_memory_sequence.add(mem1, mem2)

    engine = DreamframeRebirthEngine.objects.create(
        initiating_assistant=assistant,
        dream_sequence_log="log",
        codex_reentry_signature={"r": 1},
        ritual_rebirth_path={"p": [1]},
        new_symbolic_identity_id="new-id",
    )

    summoner = FederatedMythicIntelligenceSummoner.objects.create(
        target_network="net",
        summoning_conditions={"c": 1},
        symbolic_merge_index=0.7,
        narrative_convergence_path="path",
    )
    summoner.assistant_manifest.add(assistant)

    assert layer.temporal_memory_sequence.count() == 2
    assert engine.initiating_assistant == assistant
    assert summoner.assistant_manifest.count() == 1
