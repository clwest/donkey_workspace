import pytest

pytest.importorskip("django")

from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    AssistantSummoningScroll,
    GuildMemoryRelayNode,
    SymbolicInterlinkMap,
)


def test_phase13_3_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="oracle")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="m", content="c")
    guild = CodexLinkedGuild.objects.create(guild_name="g", codex=codex)

    scroll = AssistantSummoningScroll.objects.create(
        scroll_title="S",
        invocation_phrase="call",
        assistant=assistant,
        scroll_url="http://x",
        symbolic_rune_tags={},
    )

    relay = GuildMemoryRelayNode.objects.create(
        linked_guild=guild,
        transmission_window="daily",
        symbolic_payload_tags={},
    )
    relay.shared_memories.add(memory)

    interlink = SymbolicInterlinkMap.objects.create(
        interlink_title="I",
        source_memory=memory,
        archetype_tags={},
    )
    interlink.linked_codices.add(codex)
    interlink.connected_assistants.add(assistant)

    assert scroll.assistant == assistant
    assert relay.shared_memories.count() == 1
    assert interlink.linked_codices.count() == 1
