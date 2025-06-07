import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from django.core.management import call_command
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, ReflectionReplayLog
from memory.utils.reflection_replay import replay_reflection

class DriftedReplayCLITest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Tester", slug="tester")
        SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            summary="Discussing EVM design",
            title="t",
        )
        self.replay = replay_reflection(self.reflection)
        self.replay.reflection_score = 0.7
        self.replay.save(update_fields=["reflection_score"])

    def test_drifted_command(self):
        call_command("replay_drifted_reflections", assistant="tester")
        self.assertGreater(
            ReflectionReplayLog.objects.filter(assistant=self.assistant).count(),
            1,
        )
        new_replay = (
            ReflectionReplayLog.objects.filter(assistant=self.assistant)
            .order_by("-created_at")
            .first()
        )
        self.assertTrue(new_replay.is_priority)
