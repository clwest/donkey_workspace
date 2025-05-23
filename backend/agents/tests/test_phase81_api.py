import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry


class Phase81APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_create_purpose_radiance(self):
        resp = self.client.post(
            "/api/v1/agents/purpose-radiance/",
            {
                "assistant": self.assistant.id,
                "emitted_frequency": 1.0,
                "narrative_alignment_vector": {"x": 1},
                "symbolic_beacon_tags": ["tag"],
                "pulse_intensity": 0.7,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/purpose-radiance/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_gravity_well(self):
        resp = self.client.post(
            "/api/v1/agents/gravity-wells/",
            {
                "source_memory": self.memory.id,
                "influence_radius": 3.0,
                "distortion_effects": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/gravity-wells/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_memory_harmonics(self):
        resp = self.client.post(
            "/api/v1/agents/memory-harmonics/",
            {
                "pulse_id": "p1",
                "phase_coherence_level": 0.9,
                "symbolic_tuning_notes": "n",
                "linked_assistants": [self.assistant.id],
                "applied_to_memory": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/memory-harmonics/")
        self.assertEqual(len(list_resp.json()), 1)
