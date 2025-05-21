import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread


class ThreadContinuitySuggestionTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="T1")
        self.other = NarrativeThread.objects.create(title="T2")

    def test_suggest_continuity_api(self):
        url = f"/api/mcp/threads/{self.thread.id}/suggest-continuity/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("continuity_summary", data)
        self.assertIn("link_suggestions", data)
        self.thread.refresh_from_db()
        self.assertIsNotNone(self.thread.continuity_summary)
