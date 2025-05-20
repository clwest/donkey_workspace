import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
import uuid

from assistants.models import Assistant, ChatSession, DelegationEvent
from tools.models import Tool
from assistants.utils.delegation import spawn_delegated_assistant
from memory.models import MemoryEntry


class DelegationEventCreationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="creator", password="pw")
        self.parent = Assistant.objects.create(name="Parent", specialty="root", created_by=self.user)
        self.session = ChatSession.objects.create(assistant=self.parent, session_id=uuid.uuid4())
        self.memory = MemoryEntry.objects.create(event="Trigger", assistant=self.parent, chat_session=self.session)
        self.tool = Tool.objects.create(name="Echo", slug="echo")

    def test_event_created_with_summary_and_reason(self):
        child = spawn_delegated_assistant(
            self.session,
            name="Child",
            memory_entry=self.memory,
            reason="token_limit",
            summary="hit limit",
            triggered_by_tool=self.tool,
        )
        event = DelegationEvent.objects.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.parent_assistant, self.parent)
        self.assertEqual(event.child_assistant, child)
        self.assertEqual(event.triggering_session, self.session)
        self.assertEqual(event.triggering_memory, self.memory)
        self.assertEqual(event.reason, "token_limit")
        self.assertEqual(event.summary, "hit limit")
        self.assertEqual(event.triggered_by_tool, self.tool)
