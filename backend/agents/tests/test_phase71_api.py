import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry


class Phase71APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_create_anomaly(self):
        resp = self.client.post(
            "/api/v1/agents/anomalies/",
            {
                "assistant": self.assistant.id,
                "anomaly_type": "drift",
                "detected_by": "system",
                "symbolic_trace": "trace",
                "memory_reference": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/anomalies/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_belief_recovery(self):
        resp = self.client.post(
            "/api/v1/agents/belief-recovery/",
            {
                "assistant": self.assistant.id,
                "initiating_memory": self.memory.id,
                "collapse_type": "paradox",
                "ritual_steps": {},
                "restored_alignment": {},
                "successful": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/belief-recovery/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_multiverse_loop(self):
        resp = self.client.post(
            "/api/v1/agents/multiverse-loops/",
            {
                "linked_timelines": ["t1", "t2"],
                "anchor_assistant": self.assistant.id,
                "loop_reason": "sync",
                "echo_transfer_summary": "done",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/multiverse-loops/")
        self.assertEqual(len(list_resp.json()), 1)
