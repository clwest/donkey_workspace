import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from django.core.management import call_command
from assistants.models import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from memory.models import ReplayThreadLog, DriftAnalysisSnapshot


class SymbolicReplayTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Godel", slug="godelbot")
        AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="Consider the incompleteness theorem",
        )

    def test_replay_creates_logs(self):
        call_command("run_symbolic_replay", assistant="godelbot")
        self.assertEqual(ReplayThreadLog.objects.filter(assistant=self.assistant).count(), 1)
        replay = ReplayThreadLog.objects.filter(assistant=self.assistant).first()
        snaps = DriftAnalysisSnapshot.objects.filter(replay_log=replay)
        self.assertGreaterEqual(snaps.count(), 1)
        for s in snaps:
            self.assertGreaterEqual(s.drift_score, 0.0)
            self.assertLessEqual(s.drift_score, 1.0)
