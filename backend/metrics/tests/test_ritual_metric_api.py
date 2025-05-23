import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from agents.models import RitualArchiveEntry
from metrics.models import RitualPerformanceMetric


class RitualPerformanceMetricAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.ritual = RitualArchiveEntry.objects.create(
            name="R", ceremony_type="test"
        )

    def test_create_metric(self):
        resp = self.client.post(
            "/api/metrics/ritual-metrics/",
            {
                "ritual": self.ritual.id,
                "assistant": self.assistant.id,
                "symbolic_score": 0.8,
                "transformation_alignment": 0.9,
                "mythic_tags": {},
                "reflection_notes": "good",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(RitualPerformanceMetric.objects.count(), 1)
