import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from django.core.management import call_command
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor

class ReflectionReplayTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Tester", slug="tester")
        self.anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            summary="Discussing the EVM design",
            title="t",
        )

    def test_replay_reflection_creates_log(self):
        from memory.utils.reflection_replay import replay_reflection

        replay = replay_reflection(self.reflection)
        self.assertIsNotNone(replay)
        self.assertEqual(replay.original_reflection, self.reflection)

        self.reflection.refresh_from_db()
        self.assertIn(self.anchor, self.reflection.related_anchors.all())
        self.assertEqual(replay.changed_anchors, [self.anchor.slug])


    def test_cli_replay(self):
        call_command("replay_reflections", assistant="tester", since="1d")
        self.assertEqual(
            ReflectionReplayLog.objects.filter(assistant=self.assistant).count(),
            1,
        )
        replay = ReflectionReplayLog.objects.filter(assistant=self.assistant).first()
        self.assertEqual(replay.reflection_score, 0.0)
