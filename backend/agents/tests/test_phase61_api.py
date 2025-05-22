import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import CollaborationThread


class Phase61APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u61", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")

    def test_create_collaboration_thread(self):
        resp = self.client.post(
            "/api/agents/collaboration-threads/",
            {
                "title": "T",
                "narrative_focus": "n",
                "symbolic_tags": {},
                "participants": [self.a1.id, self.a2.id],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/agents/collaboration-threads/")
        self.assertEqual(len(list_resp.json()), 1)
