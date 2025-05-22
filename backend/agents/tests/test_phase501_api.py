import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry


class Phase501APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_create_tribunal_case(self):
        resp = self.client.post(
            "/api/v1/tribunals/",
            {
                "issue_type": "breach",
                "reflective_summary": "s",
                "involved_assistants": [self.assistant.id],
                "memory_evidence": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/tribunals/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_restorative_memory_action(self):
        resp = self.client.post(
            "/api/v1/restorative-memory/",
            {
                "initiating_assistant": self.assistant.id,
                "damaged_memory": self.memory.id,
                "reformation_notes": "fix",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/restorative-memory/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_reputation_regeneration_event(self):
        resp = self.client.post(
            "/api/v1/reputation-rebirths/",
            {
                "assistant": self.assistant.id,
                "reflection_cycle_reference": self.memory.id,
                "change_summary": "improved",
                "symbolic_rebirth_tags": {},
                "regenerated_score": 0.5,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/reputation-rebirths/")
        self.assertEqual(len(list_resp.json()), 1)
