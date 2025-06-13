import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorConfidenceLog


class AnchorConfidenceEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="term1",
            label="Term1",
            memory_context=self.assistant.memory_context,
        )
        AnchorConfidenceLog.objects.create(
            anchor=self.anchor,
            assistant=self.assistant,
            total_logs=10,
            fallback_rate=0.6,
            avg_score=0.3,
            glossary_hit_pct=0.2,
            score_delta_avg=0.1,
        )

    def test_confidence_endpoint(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchors/confidence/"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["slug"], "term1")

    def test_filter_severity(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchors/confidence/",
            {"severity": "high"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchors/confidence/",
            {"severity": "medium"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchors/confidence/",
            {"severity": "low"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)

