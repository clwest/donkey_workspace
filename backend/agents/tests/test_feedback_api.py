import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from agents.models import Agent, AgentFeedbackLog


class AgentFeedbackAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.agent = Agent.objects.create(name="Agent", slug="agent")

    def test_update_from_feedback(self):
        url = f"/api/v1/agents/{self.agent.id}/update-from-feedback/"
        resp = self.client.post(
            url,
            {"feedback": [{"feedback_text": "great", "score": 0.9}]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AgentFeedbackLog.objects.count(), 1)
