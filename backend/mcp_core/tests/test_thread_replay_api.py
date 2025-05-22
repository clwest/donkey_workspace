import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mcp_core.models import NarrativeThread
from memory.models import MemoryEntry
from assistants.models import AssistantThoughtLog, AssistantReflectionLog


class ThreadReplayAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.thread = NarrativeThread.objects.create(title="R")
        self.mem = MemoryEntry.objects.create(event="m1", thread=self.thread)
        self.thought = AssistantThoughtLog.objects.create(
            thought="t1", narrative_thread=self.thread
        )
        self.reflect = AssistantReflectionLog.objects.create(
            summary="r1", title="R1", linked_memory=self.mem
        )

    def test_thread_replay_endpoint(self):
        url = f"/api/v1/threads/{self.thread.id}/replay/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        types = {item["type"] for item in data}
        self.assertSetEqual(types, {"memory", "thought", "reflection"})
