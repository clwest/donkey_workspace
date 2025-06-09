import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.assistant import AssistantChatMessage
from mcp_core.models import Tag
from memory.models import MemoryEntry

class DemoChatAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="Demo",
            slug="demo",
            tone="friendly",
            is_demo=True,
        )
        tag = Tag.objects.create(slug="starter-chat", name="starter-chat")
        mem = MemoryEntry.objects.create(
            assistant=self.assistant,
            full_transcript="User: Hi\nAssistant: Welcome!",
            is_demo=True,
        )
        mem.tags.add(tag)

    def test_intro_and_starter_memory(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/chat/?starter_query=Hello"
        resp = self.client.post(
            url,
            {"message": "__ping__", "session_id": "s1", "demo_session_id": "d1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("demo_intro_message", data)
        self.assertIn("starter_memory", data)
        self.assertTrue(len(data["starter_memory"]) > 0)
        self.assertTrue("Welcome" in data["demo_intro_message"])
        self.assertEqual(data["messages"][0]["content"], "Hello")

    def test_demo_not_persisted(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/chat/"
        self.client.post(
            url,
            {
                "message": "hey",
                "session_id": "s2",
                "demo_session_id": "d2",
            },
            format="json",
        )
        self.assertEqual(AssistantChatMessage.objects.count(), 0)
        # starter memory only
        self.assertEqual(MemoryEntry.objects.filter(assistant=self.assistant).count(), 1)

    def test_no_starter_memory_without_param(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/chat/"
        resp = self.client.post(
            url,
            {"message": "__ping__", "session_id": "s3", "demo_session_id": "d3"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("starter_memory"), [])
