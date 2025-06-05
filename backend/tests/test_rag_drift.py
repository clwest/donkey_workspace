import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import RAGGroundingLog

class RagDriftReportTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.client = APIClient()

    def test_rag_drift_report(self):
        for _ in range(3):
            RAGGroundingLog.objects.create(
                assistant=self.assistant,
                fallback_triggered=True,
                expected_anchor="evm",
                adjusted_score=0.1,
            )
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/rag_drift_report/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["term"], "evm")
        self.assertEqual(resp.data[0]["fallback_count"], 3)
        self.assertEqual(resp.data[0]["risk"], "high")
