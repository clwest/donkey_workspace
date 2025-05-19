import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant, AssistantReflectionLog
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread

class AssistantMemoryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="test")
        self.thread = NarrativeThread.objects.create(title="T")
        MemoryEntry.objects.create(event="one", assistant=self.assistant, summary="first", narrative_thread=self.thread)
        MemoryEntry.objects.create(event="two", assistant=self.assistant, summary="second", narrative_thread=self.thread)

    def test_list_memories(self):
        url = f"/api/assistants/{self.assistant.slug}/memories/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertIn("summary", data[0])
        self.assertIn("token_count", data[0])

    def test_reflect_now_creates_log(self):
        mem = MemoryEntry.objects.create(event="three", assistant=self.assistant, summary="third")
        url = f"/api/assistants/{self.assistant.slug}/reflect_now/"
        resp = self.client.post(url, {"memory_id": str(mem.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AssistantReflectionLog.objects.filter(assistant=self.assistant).count(), 1)
