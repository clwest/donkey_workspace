import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.test import TestCase
from unittest.mock import patch
from assistants.models import Assistant, AssistantThoughtLog
from mcp_core.models import NarrativeThread
from memory.models import MemoryEntry
from memory.utils.replay import replay_scene


class ReplaySceneUtilTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="x")
        self.thread = NarrativeThread.objects.create(title="T")
        MemoryEntry.objects.create(
            event="e1",
            summary="s1",
            assistant=self.assistant,
            thread=self.thread,
            importance=8,
        )
        MemoryEntry.objects.create(
            event="e2",
            summary="s2",
            assistant=self.assistant,
            thread=self.thread,
            importance=5,
        )

    def test_replay_scene_format(self):
        block, mems = replay_scene(self.thread.id, self.assistant)
        self.assertIn("Past Highlights", block)
        self.assertEqual(len(mems), 2)


class ChatWithSceneAPITest(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="B", specialty="y")
        self.thread = NarrativeThread.objects.create(title="Scene")
        MemoryEntry.objects.create(
            event="e", summary="sum", assistant=self.assistant, thread=self.thread
        )
        self.url = f"/api/assistants/{self.assistant.slug}/chat_with_scene/"

    @patch("assistants.views.scene.call_llm")
    def test_chat_with_scene(self, mock_call):
        mock_call.return_value = "reply"
        resp = self.client.post(
            self.url, {"thread_id": str(self.thread.id), "message": "hi"}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("reply", resp.json())
        log = AssistantThoughtLog.objects.filter(
            assistant=self.assistant, replayed_thread=self.thread
        ).first()
        self.assertIsNotNone(log)
