import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from agents.models import MythDiplomacySession
from assistants.models import AssistantCouncil


class SwarmTreatiesAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_empty_list(self):
        resp = self.client.get("/api/v1/agents/swarm-treaties/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_returns_sessions(self):
        council = AssistantCouncil.objects.create(name="C1")
        session = MythDiplomacySession.objects.create(topic="Pact", status="open")
        session.factions.add(council)
        resp = self.client.get("/api/v1/agents/swarm-treaties/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Pact")
        self.assertEqual(data[0]["participants"], ["C1"])
        self.assertEqual(data[0]["status"], "open")
