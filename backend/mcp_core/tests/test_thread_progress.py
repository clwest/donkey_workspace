import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread
from project.models import Project


class ThreadProgressAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u")
        self.thread = NarrativeThread.objects.create(title="Progress")
        Project.objects.create(user=self.user, title="P", thread=self.thread)

    def test_progress_endpoint(self):
        url = f"/api/mcp/threads/{self.thread.id}/progress/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("progress_percent", data)
        self.assertIn("completion_status", data)
