import pytest

pytest.importorskip("django")

from assistants.models import Assistant, MythCommunityCluster, CodexLinkedGuild
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    PublicMemoryGrove,
    SharedRitualCalendar,
    SymbolicReflectionArena,
)


def test_phase12_5_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(
        title="C", created_by=assistant, symbolic_domain="myth"
    )
    memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    cluster = MythCommunityCluster.objects.create(cluster_name="core")
    guild = CodexLinkedGuild.objects.create(guild_name="g", codex=codex)

    grove = PublicMemoryGrove.objects.create(
        grove_name="Grove",
        linked_cluster=cluster,
        codex_reference=codex,
    )
    grove.featured_memories.add(memory)

    calendar = SharedRitualCalendar.objects.create(
        linked_guild=guild,
        event_schedule={"e": 1},
        ritual_themes={"t": 2},
        codex_cycle_marker="cycle",
    )

    arena = SymbolicReflectionArena.objects.create(
        arena_name="Arena",
        participants={"a": 1},
        reflection_topic="topic",
        codex_focus=codex,
        summary_log="s",
    )

    assert grove.featured_memories.count() == 1
    assert calendar.linked_guild == guild
    assert arena.codex_focus == codex
