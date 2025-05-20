import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantThoughtLog, SpecializationDriftLog
from assistants.utils.drift_detection import analyze_drift_for_assistant


class SpecializationDriftTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="DriftBot", specialty="x")
        self.assistant.initial_embedding = [1.0] * 1536
        self.assistant.save()

    def test_drift_log_created(self):
        for i in range(25):
            AssistantThoughtLog.objects.create(
                assistant=self.assistant,
                thought=f"t{i}",
                embedding=[0.0] * 1536,
            )
        log = analyze_drift_for_assistant(self.assistant, threshold=0.9)
        self.assertIsNotNone(log)
        self.assertEqual(SpecializationDriftLog.objects.count(), 1)
