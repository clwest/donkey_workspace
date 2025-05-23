import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry


class Phase115APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_create_memory_echo_effect(self):
        resp = self.client.post(
            "/api/memory-echo-effects/",
            {
                "memory": self.memory.id,
                "trigger_type": "ritual",
                "visual_effect": "sparkle",
                "entropy_strength": 0.5,
                "particle_mode": "glow",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/memory-echo-effects/")
        self.assertEqual(len(list_resp.json()), 1)

