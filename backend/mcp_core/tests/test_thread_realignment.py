import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread, ThreadDiagnosticLog
from assistants.models import Assistant, AssistantThoughtLog
from assistants.utils.planning_alignment import suggest_planning_realignment


class RealignmentUtilTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="R")
        self.assistant = Assistant.objects.create(name="A", specialty="t")

    def test_suggest_planning_realignment(self):
        moods = ["optimistic", "concerned", "concerned"]
        for m in moods:
            AssistantThoughtLog.objects.create(
                assistant=self.assistant,
                thought="t",
                mood=m,
                narrative_thread=self.thread,
            )
        self.thread.continuity_score = 0.3
        self.thread.continuity_summary = "low"
        res = suggest_planning_realignment(
            self.thread,
            AssistantThoughtLog.objects.filter(narrative_thread=self.thread),
        )
        assert "summary" in res


class RealignmentAPITest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="T")
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="t",
            mood="neutral",
            narrative_thread=self.thread,
        )

    def test_realign_endpoint(self):
        url = f"/api/mcp/threads/{self.thread.id}/realign/"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert ThreadDiagnosticLog.objects.filter(
            thread=self.thread, type="realignment_suggestion"
        ).count() == 1

