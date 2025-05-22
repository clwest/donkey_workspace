import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from metrics.models import PerformanceMetric


class PerformanceDashboardAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        PerformanceMetric.objects.create(
            assistant=self.assistant, name="latency_ms", value=1.2
        )

    def test_dashboard_endpoint(self):
        url = f"/api/v1/metrics/performance/{self.assistant.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("metrics", data)
        self.assertEqual(len(data["metrics"]), 1)
