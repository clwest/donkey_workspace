import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from django.utils import timezone
from mcp_core.models import NarrativeThread, ThreadDiagnosticLog
from assistants.models import Assistant, AssistantThoughtLog
from memory.models import MemoryEntry
from mcp_core.utils.thread_diagnostics import run_thread_diagnostics


class ThreadDiagnosticUtilTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="Diag")
        self.assistant = Assistant.objects.create(name="A", specialty="t")

    def test_run_thread_diagnostics(self):
        MemoryEntry.objects.create(event="e", thread=self.thread)
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="t",
            narrative_thread=self.thread,
        )
        result = run_thread_diagnostics(self.thread)
        self.thread.refresh_from_db()
        assert "score" in result
        assert self.thread.continuity_score is not None
        assert ThreadDiagnosticLog.objects.filter(thread=self.thread).count() == 1


class ThreadDiagnosticAPITest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="T")

    def test_diagnose_endpoint(self):
        resp = self.client.post(f"/api/v1/mcp/threads/{self.thread.id}/diagnose/", {})
        assert resp.status_code == 200
        self.thread.refresh_from_db()
        assert self.thread.continuity_score is not None

    def test_list_diagnostics(self):
        run_thread_diagnostics(self.thread)
        resp = self.client.get(f"/api/v1/mcp/threads/{self.thread.id}/diagnostics/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1
