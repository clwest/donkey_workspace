import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SwarmCodex, SwarmMemoryEntry


class Phase57APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_create_archetype_evolution_event(self):
        resp = self.client.post(
            "/api/v1/agents/archetype-evolution/",
            {
                "assistant": self.assistant.id,
                "previous_archetype": "sage",
                "new_archetype": "oracle",
                "trigger_memory": self.memory.id,
                "symbolic_justification": "vision",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/archetype-evolution/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_codex_symbol_reconciliation(self):
        resp = self.client.post(
            "/api/v1/agents/codex-symbol-reconciliation/",
            {
                "conflicting_symbol": "dragon",
                "proposed_resolution": "merge meaning",
                "affected_codices": [self.codex.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/v1/agents/codex-symbol-reconciliation/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_myth_api_lookup(self):
        resp = self.client.get("/api/v1/agents/myth-api/lookup/?q=m")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("codices", resp.json())
