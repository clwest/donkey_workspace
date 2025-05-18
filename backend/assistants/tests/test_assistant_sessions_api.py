import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant, ChatSession
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread


class AssistantSessionsAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="test")
        thread = NarrativeThread.objects.create(title="T")
        self.s1 = ChatSession.objects.create(assistant=self.assistant, narrative_thread=thread)
        self.s2 = ChatSession.objects.create(assistant=self.assistant, narrative_thread=thread)
        MemoryEntry.objects.create(event="m1", assistant=self.assistant, chat_session=self.s1, summary="s1")
        MemoryEntry.objects.create(event="m2", assistant=self.assistant, chat_session=self.s2, summary="s2")

    def test_sessions_for_assistant(self):
        url = f"/api/assistants/{self.assistant.slug}/sessions/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("sessions", data)
        self.assertEqual(len(data["sessions"]), 2)
        self.assertIn("memory_summaries", data)
        self.assertEqual(len(data["memory_summaries"]), 2)
        self.assertIn("threads", data)
        self.assertTrue(len(data["threads"]) >= 1)
