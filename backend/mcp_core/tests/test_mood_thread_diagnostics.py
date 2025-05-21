import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread, ThreadDiagnosticLog
from assistants.models import Assistant, AssistantThoughtLog
from mcp_core.utils.thread_diagnostics import run_thread_diagnostics

class MoodThreadDiagnosticTest(APITestCase):
    def setUp(self):
        self.thread = NarrativeThread.objects.create(title="Mood T")
        self.assistant = Assistant.objects.create(name="M", specialty="t")

    def test_mood_influence_recorded(self):
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="worried",
            mood="anxious",
            narrative_thread=self.thread,
        )
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="still worried",
            mood="anxious",
            narrative_thread=self.thread,
        )
        run_thread_diagnostics(self.thread)
        log = ThreadDiagnosticLog.objects.filter(thread=self.thread).first()
        self.assertIsNotNone(log.mood_influence)
