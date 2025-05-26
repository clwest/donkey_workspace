from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from agents.models.core import Agent

class AgentDashboardAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="agent", password="pw")
        self.client.force_authenticate(user=self.user)
        Agent.objects.create(name="AgentA", slug="agenta")

    def test_list_agents_dashboard(self):
        resp = self.client.get("/api/v1/mcp/agent/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "agenta")

    def test_agent_detail_dashboard(self):
        resp = self.client.get("/api/v1/mcp/agent/agenta/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["slug"], "agenta")

