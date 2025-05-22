import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from simulation.models import SimulationConfig, SimulationRunLog


class SimulationAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.config = SimulationConfig.objects.create(
            name="Test", assistant_ids=["1", "2"], scenario_description="d", parameters={"turn_count": 1}
        )

    def test_run_endpoint(self):
        resp = self.client.post("/api/v1/simulation/run/", {"config_id": self.config.id})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("run_id", data)
        self.assertTrue(SimulationRunLog.objects.filter(id=data["run_id"]).exists())
