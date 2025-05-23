import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    StoryfieldZone,
    MythPatternCluster,
    IntentHarmonizationSession,
    SwarmMemoryEntry,
)


def test_storyfield_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    zone = StoryfieldZone.objects.create(
        zone_name="Z",
        aligned_roles={"hero": 1},
        myth_tags=["epic"],
        resonance_threshold=0.5,
    )
    zone.active_memory.add(mem)

    cluster = MythPatternCluster.objects.create(
        cluster_id="C1",
        pattern_summary="p",
        symbolic_signature="sig",
        convergence_score=0.7,
    )
    cluster.linked_memories.add(mem)

    session = IntentHarmonizationSession.objects.create(
        coordination_focus="f",
        proposed_strategies=["s"],
        symbolic_alignment_score=0.8,
    )
    session.involved_assistants.add(assistant)

    assert zone.active_memory.count() == 1
    assert cluster.linked_memories.count() == 1
    assert session.involved_assistants.count() == 1
