import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread, ThreadObjectiveReflection


class ThreadObjectiveAPITestCase(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="T1")

    def test_set_and_get_objective(self):
        url = f"/api/v1/mcp/threads/{self.thread.id}/set_objective/"
        resp = self.client.post(url, {"objective": "Build"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.long_term_objective, "Build")

        get_url = f"/api/v1/mcp/threads/{self.thread.id}/objective/"
        resp = self.client.get(get_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["objective"], "Build")

    def test_reflection_creation(self):
        resp = self.client.post(f"/api/v1/mcp/threads/{self.thread.id}/reflect/")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(
            ThreadObjectiveReflection.objects.filter(thread=self.thread).count(),
            1,
        )
