
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantReflectionLog
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread, Tag


class AssistantMemoryAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="test")
        self.thread = NarrativeThread.objects.create(title="T")
        tag = Tag.objects.create(name="planning", slug="planning")
        m1 = MemoryEntry.objects.create(
            event="one",
            assistant=self.assistant,
            summary="first",
            narrative_thread=self.thread,
            emotion="curious",
        )
        m2 = MemoryEntry.objects.create(
            event="two",
            assistant=self.assistant,
            summary="second",
            narrative_thread=self.thread,
            emotion="thoughtful",
        )
        m1.tags.add(tag)
        m2.tags.add(tag)

    def test_list_memories(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/memories/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertIn("summary", data[0])
        self.assertIn("token_count", data[0])

    def test_reflect_now_creates_log(self):
        mem = MemoryEntry.objects.create(
            event="three", assistant=self.assistant, summary="third"
        )
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect_now/"
        resp = self.client.post(url, {"memory_id": str(mem.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            AssistantReflectionLog.objects.filter(assistant=self.assistant).count(), 1
        )

    def test_memory_summary_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/memory/summary/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["most_recent"]), 2)
        self.assertIn("planning", data["recent_tags"])
