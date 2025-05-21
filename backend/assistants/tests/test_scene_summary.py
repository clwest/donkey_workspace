import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from story.models import NarrativeEvent
from assistants.models import Assistant, AssistantThoughtLog, DelegationEvent, ChatSession
from memory.models import MemoryEntry
from mcp_core.utils.scene_summary import summarize_scene_context
import uuid


class SceneSummaryTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.assistant = Assistant.objects.create(name="A", specialty="s", created_by=self.user)
        self.event = NarrativeEvent.objects.create(title="Scene")
        self.session = ChatSession.objects.create(assistant=self.assistant, session_id=uuid.uuid4())
        for i in range(5):
            AssistantThoughtLog.objects.create(
                assistant=self.assistant,
                thought=f"thought {i}",
                linked_event=self.event,
                mood="curious",
            )
        for i in range(2):
            d = DelegationEvent.objects.create(
                parent_assistant=self.assistant,
                child_assistant=self.assistant,
                reason=f"reason {i}",
            )
            DelegationEvent.objects.filter(id=d.id).update(created_at=self.event.timestamp)
        for i in range(3):
            MemoryEntry.objects.create(event=f"memory {i}", timestamp=self.event.timestamp)

    @patch("mcp_core.utils.scene_summary.call_llm")
    def test_scene_summary_saved(self, mock_call):
        mock_call.return_value = "summary text"
        summarize_scene_context(self.event)
        self.event.refresh_from_db()
        self.assertEqual(self.event.scene_summary, "summary text")
        self.assertTrue(self.event.summary_generated)
        mock_call.assert_called()

