import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, GlossaryKeeperLog


class KeeperLogEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A", slug="claritybot")
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="term",
            label="Term",
            assistant=self.assistant,
            memory_context=self.assistant.memory_context,
            suggested_label="Better",
        )
        GlossaryKeeperLog.objects.create(
            anchor=self.anchor,
            assistant=self.assistant,
            action_taken="suggest_mutation",
        )
        GlossaryKeeperLog.objects.create(
            anchor=self.anchor,
            assistant=self.assistant,
            action_taken="reflection_written",
        )

    def test_keeper_log_list(self):
        resp = self.client.get("/api/keeper/logs/?assistant=claritybot")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["assistant_slug"], "claritybot")
        self.assertEqual(data[0]["anchor_slug"], "term")
        self.assertIn("suggested_label", data[0])

    def test_action_filter(self):
        resp = self.client.get("/api/keeper/logs/?action=suggest_mutation")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["action_taken"], "suggest_mutation")
