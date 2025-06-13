import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from memory.models import RAGGroundingLog, RAGDiagnosticLog
from django.core.management import call_command
from unittest.mock import patch


class AssistantDiagnosticAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_endpoint_returns_latest_report(self):
        assistant = Assistant.objects.create(name="Diag", slug="diag", is_demo=True)
        RAGGroundingLog.objects.create(
            assistant=assistant, query="q1", fallback_triggered=True
        )
        RAGGroundingLog.objects.create(
            assistant=assistant, query="q2", fallback_triggered=False
        )
        RAGDiagnosticLog.objects.create(
            assistant=assistant, query_text="q1", confidence_score_avg=0.6
        )
        with patch(
            "assistants.management.commands.generate_diagnostic_reports.call_command"
        ):
            call_command("generate_diagnostic_reports")
        resp = self.client.get(f"/api/assistants/{assistant.slug}/diagnostic_report/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("fallback_rate", data)
        self.assertAlmostEqual(data["fallback_rate"], 0.5, places=2)
        self.assertIn("certified_rag_ready", data)
