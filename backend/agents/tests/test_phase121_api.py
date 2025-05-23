import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    MemoryInheritanceSeed,
)


class Phase121APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u121", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_create_personal_anchor(self):
        resp = self.client.post(
            "/api/v1/agents/codex/personal/",
            {
                "user_id": "u121",
                "codex": self.codex.id,
                "symbolic_statements": {},
                "anchor_strength": 0.7,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/codex/personal/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_ritual_contract(self):
        resp = self.client.post(
            "/api/v1/agents/ritual/contracts/",
            {
                "assistant": self.assistant.id,
                "user_id": "u121",
                "contract_terms": "t",
                "codex_link": self.codex.id,
                "shared_memory": [self.memory.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/ritual/contracts/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_get_inherited_memory(self):
        seed = MemoryInheritanceSeed.objects.create(
            user_id="u121", narrative_path="p", symbolic_tags={}
        )
        seed.onboarding_memory.add(self.memory)
        resp = self.client.get(
            f"/api/v1/agents/assistants/{seed.user_id}/memory/inherited/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
