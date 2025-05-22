import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from agents.models import Agent


class AgentListAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Assist", slug="assist")
        Agent.objects.create(
            name="A1",
            slug="a1",
            parent_assistant=self.assistant,
        )

    def test_list_agents(self):
        resp = self.client.get("/api/v1/agents/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        agent = data[0]
        self.assertIn("parent_assistant_id", agent)
        self.assertEqual(agent["parent_assistant_id"], str(self.assistant.id))
        self.assertEqual(agent["name"], "A1")
        self.assertEqual(agent["slug"], "a1")

