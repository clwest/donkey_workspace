import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, TranscendentMyth


class Phase92APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Alpha")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")
        self.myth = TranscendentMyth.objects.create(name="Myth")

    def test_archetype_genesis_endpoint(self):
        resp = self.client.post(
            "/api/archetype-genesis/",
            {
                "assistant": self.assistant.id,
                "memory_path": [self.memory.id],
                "seed_purpose": "quest",
                "resulting_archetype": "hero",
                "symbolic_signature": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/archetype-genesis/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_myth_bloom_endpoint(self):
        resp = self.client.post(
            "/api/myth-blooms/",
            {
                "bloom_name": "B",
                "origin_trigger": self.myth.id,
                "participating_agents": [self.assistant.id],
                "symbolic_flow_summary": "s",
                "reflected_memory": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/myth-blooms/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_belief_seeds_endpoint(self):
        resp = self.client.post(
            "/api/belief-seeds/",
            {
                "originating_entity": self.assistant.id,
                "core_symbol_set": {},
                "intended_recipients": [self.assistant.id],
                "propagation_log": "log",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/belief-seeds/")
        self.assertEqual(len(list_resp.json()), 1)
