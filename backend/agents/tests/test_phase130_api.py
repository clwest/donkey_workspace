import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmCodex, SwarmMemoryEntry


class Phase130APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u130", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_onboarding_flow(self):
        resp = self.client.post(
            "/api/agents/onboarding/",
            {
                "assistant": {"name": "NewA", "specialty": "s"},
                "identity_card": {
                    "archetype": "arch",
                    "symbolic_tags": [],
                    "myth_path": "p",
                    "purpose_signature": "sig",
                },
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

    def test_world_timeline(self):
        resp = self.client.get("/api/agents/timeline/")
        self.assertEqual(resp.status_code, 200)

    def test_assistant_rebirth(self):
        resp = self.client.post(
            f"/api/agents/assistants/{self.assistant.id}/rebirth/",
            {"name": "Reborn"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
