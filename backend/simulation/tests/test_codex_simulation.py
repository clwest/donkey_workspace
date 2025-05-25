import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from simulation.models import CodexSimulationScenario
from agents.models import SwarmCodex
from assistants.models import Assistant


class CodexSimulationAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="a", specialty="x")
        self.codex = SwarmCodex.objects.create(title="c", created_by=self.assistant)

    def test_create_scenario(self):
        resp = self.client.post(
            "/api/v1/simulation/codex/simulate/",
            {"name": "s", "baseline_codex": self.codex.id, "mutated_clauses": []},
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(CodexSimulationScenario.objects.count(), 1)
