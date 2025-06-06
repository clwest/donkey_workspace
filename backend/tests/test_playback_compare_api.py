import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor
from memory.utils.reflection_replay import replay_reflection


class PlaybackCompareAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="Tester", slug="tester")
        SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            summary="Discussing EVM design",
            title="t",
        )
        self.replay = replay_reflection(self.reflection)

    def test_compare_endpoint(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/rag_playback/compare/{self.replay.id}/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("replay_chunks", resp.data)
