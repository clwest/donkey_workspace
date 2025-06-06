import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor
from memory.utils.reflection_replay import replay_reflection


class ReplayDiffAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="Tester", slug="tester")
        self.anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="EVM")
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            summary="Discussing EVM design",
            title="t",
        )
        self.replay = replay_reflection(self.reflection)
        self.replay.replayed_summary = "Updated summary about the EVM upgrade"
        self.replay.save(update_fields=["replayed_summary"])
        self.anchor.refresh_from_db()
        self.assertEqual(self.anchor.acquisition_stage, "acquired")

    def test_diff_endpoint(self):
        resp = self.client.get(
            f"/api/assistants/{self.assistant.slug}/replays/{self.replay.id}/diff/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("diff_html", resp.data)

    def test_accept_and_reject(self):
        resp = self.client.post(f"/api/replays/{self.replay.id}/accept/")
        self.assertEqual(resp.status_code, 200)
        self.replay.refresh_from_db()
        self.reflection.refresh_from_db()
        self.assertEqual(self.replay.status, "accepted")
        self.assertEqual(self.reflection.summary, self.replay.replayed_summary)

        resp2 = self.client.post(f"/api/replays/{self.replay.id}/reject/")
        self.assertEqual(resp2.status_code, 200)
        self.replay.refresh_from_db()
        self.assertEqual(self.replay.status, "skipped")
