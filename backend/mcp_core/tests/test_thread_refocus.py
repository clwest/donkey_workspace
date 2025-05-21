import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread
from assistants.models import AssistantThoughtLog


class ThreadRefocusAPITest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="T1")

    def test_diagnose_creates_refocus(self):
        url = f"/api/mcp/threads/{self.thread.id}/diagnose/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.thread.refresh_from_db()
        self.assertIsNotNone(self.thread.last_refocus_prompt)
        self.assertGreaterEqual(
            AssistantThoughtLog.objects.filter(
                narrative_thread=self.thread, thought_type="refocus"
            ).count(),
            1,
        )
        data = resp.json()
        self.assertIn("continuity_score", data)
        self.assertIn("refocus_prompt", data)

    def test_manual_refocus_endpoint(self):
        url = f"/api/mcp/threads/{self.thread.id}/refocus/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(
            AssistantThoughtLog.objects.filter(
                narrative_thread=self.thread, thought_type="refocus"
            ).count(),
            1,
        )
