import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model

from assistants.models import Assistant
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
        self.assistant = Assistant.objects.create(name="Prophet", specialty="seer", created_by=self.user)
        self.civ = AssistantCivilization.objects.create(name="Dreamers")
        self.civ.members.add(self.assistant)
        self.mem = SwarmMemoryEntry.objects.create(title="Vision", content="omens")
        self.mem.linked_agents.add(self.assistant)

    def test_synthesize_creates_myth(self):
        result = synthesize_theology_from_memory(self.civ)
        self.assertIn("myth_id", result)
        self.assertTrue(TranscendentMyth.objects.filter(id=result["myth_id"]).exists())

    def test_cosmogenesis_event(self):
        myth = TranscendentMyth.objects.create(title="Axis", core_tenets=["x"], mythic_axis="duality")
        event = AssistantCosmogenesisEvent.objects.create(
            name="Birth",
            myth_root=myth,
            known_universes={},
        )
        self.assertEqual(event.myth_root, myth)
