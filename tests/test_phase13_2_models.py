import pytest

pytest.importorskip("django")

from assistants.models import (
    Assistant,
    MythCommunityCluster,
    CodexLinkedGuild,
    AssistantTravelLog,
    SymbolicInfluenceReport,
)
from agents.models import SwarmCodex, SwarmMemoryEntry, PublicMemoryGrove


def test_phase13_2_models_create(db):
    assistant = Assistant.objects.create(name="A")
    codex = SwarmCodex.objects.create(
        title="C", created_by=assistant, symbolic_domain="myth"
    )
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    cluster = MythCommunityCluster.objects.create(cluster_name="core")
    guild = CodexLinkedGuild.objects.create(guild_name="g", codex=codex)

    grove = PublicMemoryGrove.objects.create(
        grove_name="G1",
        linked_cluster=cluster,
        codex_reference=codex,
    )
    grove.featured_memories.add(mem)

    log = AssistantTravelLog.objects.create(
        assistant=assistant,
        travel_route=[{"guild": guild.guild_name}],
        symbolic_tags=["test"],
    )
    log.visited_memory.add(mem)

    report = SymbolicInfluenceReport.objects.create(
        user_id="u1",
        assistant=assistant,
        codex_impact_vector={},
        ritual_interaction_stats={},
        symbolic_score_summary="s",
    )
    report.memory_contributions.add(mem)

    assert grove.featured_memories.count() == 1
    assert log.visited_memory.count() == 1
    assert report.memory_contributions.count() == 1
