import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, AssistantGuild
from agents.models import SwarmMemoryEntry, TranscendentMyth


class Phase83APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.guild = AssistantGuild.objects.create(name="G")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.myth = TranscendentMyth.objects.create(name="Myth")

    def test_create_memory_realm(self):
        resp = self.client.post(
            "/api/memory-realms/",
            {
                "zone_name": "Z",
                "origin_myth": self.myth.id,
                "memory_inhabitants": [self.memory.id],
                "spatial_traits": {},
                "symbolic_navigation_tags": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/memory-realms/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_ritual_sync(self):
        resp = self.client.post(
            "/api/ritual-sync/",
            {
                "pulse_id": "p1",
                "initiating_guild": self.guild.id,
                "synchronization_targets": [self.assistant.id],
                "sync_tags": {},
                "phase_trigger": "solstice",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/ritual-sync/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_archetype_field(self):
        resp = self.client.post(
            "/api/archetype-fields/",
            {
                "cluster_name": "C",
                "anchor_roles": {},
                "participating_assistants": [self.assistant.id],
                "resonance_score": 0.7,
                "symbolic_purpose_vector": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/archetype-fields/")
        self.assertEqual(len(list_resp.json()), 1)
