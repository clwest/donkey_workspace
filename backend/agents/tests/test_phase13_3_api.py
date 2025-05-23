import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    AssistantSummoningScroll,
    GuildMemoryRelayNode,
    SymbolicInterlinkMap,
)


class Phase133APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", slug="a")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.guild = CodexLinkedGuild.objects.create(guild_name="g", codex=self.codex)
        self.scroll = AssistantSummoningScroll.objects.create(
            scroll_title="S",
            invocation_phrase="call",
            assistant=self.assistant,
            scroll_url="scroll://x",
            symbolic_rune_tags={},
        )
        self.relay = GuildMemoryRelayNode.objects.create(
            linked_guild=self.guild,
            transmission_window="now",
            symbolic_payload_tags={},
        )
        self.relay.shared_memories.add(self.memory)
        self.interlink = SymbolicInterlinkMap.objects.create(
            interlink_title="I",
            source_memory=self.memory,
            archetype_tags={},
        )
        self.interlink.linked_codices.add(self.codex)
        self.interlink.connected_assistants.add(self.assistant)

    def test_summon_scroll_endpoint(self):
        resp = self.client.get(f"/api/v1/agents/summon/{self.scroll.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], str(self.assistant.id))

    def test_guild_memory_relay_endpoint(self):
        resp = self.client.get(f"/api/v1/agents/guilds/{self.guild.id}/memory-relay/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_memory_interlink_endpoint(self):
        resp = self.client.get("/api/v1/agents/memory/interlink/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
