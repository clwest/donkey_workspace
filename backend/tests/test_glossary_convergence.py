import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog


class GlossaryConvergenceTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.client = APIClient()
        SymbolicMemoryAnchor.objects.create(
            slug="term1",
            label="Term1",
            memory_context=self.assistant.memory_context,
        )
        SymbolicMemoryAnchor.objects.create(
            slug="term2",
            label="Term2",
            memory_context=self.assistant.memory_context,
        )
        RAGGroundingLog.objects.create(
            assistant=self.assistant,
            expected_anchor="term1",
            adjusted_score=0.9,
            fallback_triggered=False,
        )
        RAGGroundingLog.objects.create(
            assistant=self.assistant,
            expected_anchor="term2",
            adjusted_score=0.1,
            fallback_triggered=True,
        )

    def test_convergence_overview(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/glossary/convergence/"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_anchors"], 2)
        self.assertEqual(data["grounded"], 1)
        self.assertEqual(data["failing"], 1)
        self.assertEqual(len(data["anchor_stats"]), 2)

