import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    ResurrectionTimelineTracker,
    ReincarnationTreeNode,
    DirectiveMemoryNode,
    MythicCycleExporter,
    AssistantReflectionChainSystem,
    NarrativeReincarnationFramework,
)


def test_phase14_4_models_create(db):
    a1 = Assistant.objects.create(name="A1", specialty="seer")
    a2 = Assistant.objects.create(name="A2", specialty="oracle")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=a1, symbolic_domain="myth")

    exporter = MythicCycleExporter.objects.create(
        assistant=a1,
        cycle_title="Cycle",
        ritual_threads={"t": 1},
        export_format="json",
    )
    exporter.included_memory.add(memory)
    exporter.codex_snapshots.add(codex)

    chain = AssistantReflectionChainSystem.objects.create(
        chain_type="generational",
        symbolic_tags={"x": 1},
    )
    chain.linked_assistants.add(a1, a2)

    timeline = ResurrectionTimelineTracker.objects.create(
        assistant=a1,
        reincarnation_events=[{"p": 1}],
        codex_alignment_path={"c": 1},
        role_evolution_tags=["hero"],
    )
    node = ReincarnationTreeNode.objects.create(
        node_name="root",
        assistant=a1,
        symbolic_signature={},
        phase_index="14.4",
    )
    directive = DirectiveMemoryNode.objects.create(
        assistant=a1,
        purpose_statement="p",
        triggering_conditions={},
        directive_tags={},
        temporal_scope="t",
    )

    frame = NarrativeReincarnationFramework.objects.create(
        initiating_assistant=a1,
        ritual_prompt="prep",
        memory_retention_filter={},
        new_role="sage",
        appearance_variation={},
        reincarnation_node=node,
        timeline_tracker=timeline,
        directive_memory=directive,
    )

    assert exporter.included_memory.count() == 1
    assert chain.linked_assistants.count() == 2
    assert frame.reincarnation_node == node
