import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import NarrativeThread, ThreadMergeLog, ThreadSplitLog
from memory.models import MemoryEntry
from assistants.models import AssistantThoughtLog


class ThreadMergeSplitAPITest(APITestCase):
    def setUp(self):
        self.thread1 = NarrativeThread.objects.create(title="One")
        self.thread2 = NarrativeThread.objects.create(title="Two")
        self.mem1 = MemoryEntry.objects.create(event="a", thread=self.thread1)
        self.mem2 = MemoryEntry.objects.create(event="b", thread=self.thread2)

    def test_merge_threads(self):
        url = f"/api/mcp/threads/{self.thread1.id}/merge/"
        resp = self.client.post(url, {"target_thread_id": str(self.thread2.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(NarrativeThread.objects.filter(id=self.thread2.id).exists())
        self.mem2.refresh_from_db()
        self.assertEqual(self.mem2.thread_id, self.thread1.id)
        self.assertEqual(ThreadMergeLog.objects.filter(to_thread=self.thread1, from_thread=self.thread2).count(), 1)

    def test_split_thread(self):
        # add extra memories to thread1
        mem3 = MemoryEntry.objects.create(event="c", thread=self.thread1)
        mem4 = MemoryEntry.objects.create(event="d", thread=self.thread1)
        url = f"/api/mcp/threads/{self.thread1.id}/split/"
        resp = self.client.post(url, {"from_index": 2}, format="json")
        self.assertEqual(resp.status_code, 201)
        new_id = resp.json()["id"]
        new_thread = NarrativeThread.objects.get(id=new_id)
        moved = MemoryEntry.objects.filter(thread=new_thread)
        self.assertEqual(moved.count(), 2)
        self.assertEqual(ThreadSplitLog.objects.filter(original_thread=self.thread1, new_thread=new_thread).count(), 1)

