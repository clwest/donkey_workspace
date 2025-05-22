
from django.test import TestCase
from django.contrib.auth import get_user_model

from assistants.models import Assistant, AssistantGuild
from story.models import LoreEntry
from agents.models import (
    SwarmMemoryEntry,
    AssistantCivilization,
    TranscendentMyth,
    AssistantCosmogenesisEvent,
)
from assistants.utils.theology import synthesize_theology_from_memory


class TheologyEngineTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="theologian", password="pw")
        self.assistant = Assistant.objects.create(
            name="Prophet", specialty="seer", created_by=self.user
        )
        self.lore = LoreEntry.objects.create(title="Root", summary="s")
        self.guild = AssistantGuild.objects.create(name="G", founding_myth=self.lore)
        self.guild.members.add(self.assistant)
        self.civ = AssistantCivilization.objects.create(
            name="Dreamers",
            myth_root=self.lore,
            symbolic_domain="dream",
        )
        self.civ.founding_guilds.add(self.guild)
        self.mem = SwarmMemoryEntry.objects.create(title="Vision", content="omens")
        self.mem.linked_agents.add(self.assistant)

    def test_synthesize_creates_myth(self):
        result = synthesize_theology_from_memory(self.civ)
        self.assertIn("myth_id", result)
        self.assertTrue(TranscendentMyth.objects.filter(id=result["myth_id"]).exists())

    def test_cosmogenesis_event(self):
        myth = TranscendentMyth.objects.create(
            title="Axis", core_tenets=["x"], mythic_axis="duality"
        )
        event = AssistantCosmogenesisEvent.objects.create(
            name="Birth",
            myth_root=myth,
            known_universes={},
        )
        self.assertEqual(event.myth_root, myth)
