import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from unittest.mock import patch
from assistants.models import Assistant
from memory.models import RAGGroundingLog, RAGDiagnosticLog
from assistants.models.diagnostics import AssistantDiagnosticReport
from django.conf import settings


class GenerateDiagnosticReportsTest:
    def test_cli_creates_report(self, tmp_path, db):
        settings.BASE_DIR = tmp_path
        assistant = Assistant.objects.create(name="A", slug="a", is_demo=True)
        RAGGroundingLog.objects.create(
            assistant=assistant, query="q", fallback_triggered=True
        )
        RAGDiagnosticLog.objects.create(
            assistant=assistant, query_text="q", confidence_score_avg=0.5
        )
        with patch(
            "assistants.management.commands.generate_diagnostic_reports.call_command"
        ) as mock_call:
            call_command("generate_diagnostic_reports")
            mock_call.assert_called()
        report = AssistantDiagnosticReport.objects.filter(assistant=assistant).first()
        assert report is not None
        assert abs(report.fallback_rate - 1.0) < 0.01
        md_path = tmp_path / "static" / "diagnostics" / "a.md"
        assert md_path.exists()
    def test_auto_certification(self, tmp_path, db):
        settings.BASE_DIR = tmp_path
        assistant = Assistant.objects.create(name="B", slug="b", is_demo=True)
        RAGGroundingLog.objects.create(assistant=assistant, query="q", fallback_triggered=False, glossary_hits=["t"])
        with patch(
            "assistants.management.commands.generate_diagnostic_reports.call_command"
        ) as mock_call:
            call_command("generate_diagnostic_reports", "--markdown-only")
            mock_call.assert_not_called()
        assistant.refresh_from_db()
        assert assistant.certified_rag_ready is True
        assert assistant.rag_certification_date is not None
