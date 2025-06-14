import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog, AnchorReinforcementLog
from intel_core.models import Document, DocumentChunk


class AnchorHealthEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.anchor1 = SymbolicMemoryAnchor.objects.create(
            slug="term1",
            label="Term1",
            memory_context=self.assistant.memory_context,
            mutation_status="pending",
        )
        self.anchor2 = SymbolicMemoryAnchor.objects.create(
            slug="term2",
            label="Term2",
            memory_context=self.assistant.memory_context,
        )
        doc = Document.objects.create(title="Doc", content="t")
        DocumentChunk.objects.create(
            document=doc,
            order=1,
            text="t",
            tokens=1,
            fingerprint="f1",
            anchor=self.anchor1,
            is_drifting=True,
        )
        RAGGroundingLog.objects.create(
            assistant=self.assistant,
            query="q",
            used_chunk_ids=["1"],
            fallback_triggered=True,
            glossary_hits=[],
            glossary_misses=[self.anchor1.slug],
            retrieval_score=0.0,
            expected_anchor=self.anchor1.slug,
            adjusted_score=0.0,
        )
        AnchorReinforcementLog.objects.create(
            anchor=self.anchor1,
            assistant=self.assistant,
            reason="test",
            score=0.1,
        )

    def test_anchor_health_endpoint(self):
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/anchor_health/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 2)
        item = next(i for i in data if i["slug"] == "term1")
        self.assertEqual(item["fallback_count"], 1)
        self.assertEqual(item["reinforcement_count"], 1)
        self.assertEqual(item["mutation_status"], "pending")
        self.assertIn("uses", item)
        self.assertIn("fallback_rate", item)
        self.assertIn("trend", item)

    def test_status_filters(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchor_health/",
            {"status": "pending_mutation"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)

        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchor_health/",
            {"status": "high_drift"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)

        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/anchor_health/",
            {"status": "no_match"},
        )
        self.assertEqual(len(resp.json()["results"]), 1)
