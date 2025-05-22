import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mcp_core.models import NarrativeThread, ThreadSplitLog
from memory.models import MemoryEntry
from assistants.models import Assistant, AssistantThoughtLog

class MemoryRelinkAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.client.force_authenticate(user=self.user)
        self.thread_a = NarrativeThread.objects.create(title="A")
        self.thread_b = NarrativeThread.objects.create(title="B")
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.memory = MemoryEntry.objects.create(event="e", thread=self.thread_a)
        self.thought = AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="t",
            narrative_thread=self.thread_a,
            linked_memory=self.memory,
        )

    def test_relink_endpoint(self):
        url = f"/api/v1/mcp/memory/{self.memory.id}/relink/"
        resp = self.client.patch(url, {"new_thread_id": str(self.thread_b.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.memory.refresh_from_db()
        self.thought.refresh_from_db()
        self.assertEqual(self.memory.thread_id, self.thread_b.id)
        self.assertEqual(self.thought.narrative_thread_id, self.thread_b.id)
        self.assertEqual(ThreadSplitLog.objects.filter(moved_entry=self.memory).count(), 1)
