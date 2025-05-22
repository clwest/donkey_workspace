import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant
from resources.models import ResourcePrediction, ResourceBudget


class ResourceAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        ResourcePrediction.objects.create(
            assistant=self.assistant,
            predicted_tokens=100,
            predicted_compute_ms=500.0,
        )

    def test_get_prediction(self):
        url = f"/api/v1/resources/predict/{self.assistant.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["predicted_tokens"], 100)

    def test_create_budget(self):
        url = f"/api/v1/resources/allocate/{self.assistant.id}/"
        resp = self.client.post(url, {"tokens": 50, "compute_ms": 300.0})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(ResourceBudget.objects.filter(assistant=self.assistant).exists())
