import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from learning_loops.models import AdaptiveLoopConfig


class AdaptiveLoopConfigAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")

    def test_create_config(self):
        resp = self.client.post(
            "/api/adaptive-loops/configs/",
            {
                "assistant": self.assistant.id,
                "trigger_conditions": {},
                "reflection_frequency_days": 7,
                "learning_targets": {},
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AdaptiveLoopConfig.objects.count(), 1)
