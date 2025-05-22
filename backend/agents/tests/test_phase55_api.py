import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import TranscendentMyth, SwarmMemoryEntry


class Phase55APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.assistant2 = Assistant.objects.create(name="B")
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.mem = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_create_myth_cycle_binding(self):
        resp = self.client.post(
            "/api/agents/myth-cycles/",
            {
                "assistant": self.assistant.id,
                "cycle_name": "Legend",
                "related_myth": self.myth.id,
                "narrative_role": "hero",
                "cycle_phase": "origin",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/myth-cycles/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_resurrection_template(self):
        resp = self.client.post(
            "/api/agents/resurrection-templates/",
            {
                "title": "Return",
                "base_traits": {"courage": 1},
                "symbolic_tags": {},
                "seed_memory_ids": [self.mem.id],
                "recommended_archetype": "sage",
                "created_by": self.assistant.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/resurrection-templates/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_belief_continuity(self):
        resp = self.client.post(
            "/api/agents/belief-continuity/",
            {
                "outgoing_assistant": self.assistant.id,
                "incoming_assistant": self.assistant2.id,
                "values_transferred": {"virtue": "honor"},
                "memory_reference_ids": [self.mem.id],
                "ritual_type": "echo",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/belief-continuity/")
        self.assertEqual(len(list_resp.json()), 1)
