import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    CycleAnchorRegistry,
    MemoryRegenerationProtocol,
)


def test_phase14_2_models_create(db):
    assistant = Assistant.objects.create(name="B", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    anchor = CycleAnchorRegistry.objects.create(
        assistant=assistant,
        anchor_name="A1",
        role_trait_snapshot={"r": 1},
        symbolic_notes="n",
    )

    protocol = MemoryRegenerationProtocol.objects.create(
        assistant=assistant,
        trigger_codex=codex,
        regeneration_script="s",
        symbolic_success_score=0.5,
    )
    protocol.corrupted_memory_nodes.add(memory)

    assert anchor.assistant == assistant
    assert protocol.corrupted_memory_nodes.count() == 1
