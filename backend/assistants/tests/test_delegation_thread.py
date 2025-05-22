
from django.contrib.auth import get_user_model
from django.test import TestCase
import uuid

from assistants.models import Assistant, ChatSession, DelegationEvent
from assistants.utils.delegation import spawn_delegated_assistant
from assistants.helpers.chat_helper import get_or_create_chat_session
from project.models import Project
from mcp_core.models import NarrativeThread
from memory.models import MemoryEntry


class DelegationThreadTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="threader", password="pw")
        self.parent = Assistant.objects.create(name="Parent", specialty="root", created_by=self.user)
        self.thread = NarrativeThread.objects.create(title="Story", created_by=self.user)
        self.project = Project.objects.create(
            user=self.user,
            title="Parent Project",
            assistant=self.parent,
            narrative_thread=self.thread,
            thread=self.thread,
        )
        self.session = ChatSession.objects.create(
            assistant=self.parent,
            project=self.project,
            narrative_thread=self.thread,
            thread=self.thread,
            session_id=uuid.uuid4(),
        )
        self.memory = MemoryEntry.objects.create(
            event="Trigger",
            assistant=self.parent,
            chat_session=self.session,
            related_project=self.project,
            narrative_thread=self.thread,
        )

    def test_spawn_child_inherits_thread(self):
        child = spawn_delegated_assistant(
            self.session,
            name="Child",
            memory_entry=self.memory,
        )
        child_project = Project.objects.get(assistant=child)
        child_session = ChatSession.objects.get(assistant=child)

        self.assertEqual(child_project.thread_id, self.thread.id)
        self.assertEqual(child_project.narrative_thread_id, self.thread.id)
        self.assertEqual(child_session.thread_id, self.thread.id)
        self.assertEqual(child_session.narrative_thread_id, self.thread.id)

        event = DelegationEvent.objects.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.parent_assistant, self.parent)
        self.assertEqual(event.child_assistant, child)
        self.assertEqual(event.triggering_session, self.session)
        self.assertEqual(event.triggering_memory, self.memory)
        self.assertEqual(event.triggering_session.thread_id, self.thread.id)


class ChatSessionHelperTest(TestCase):
    def test_existing_session_thread_update(self):
        session = ChatSession.objects.create(session_id=uuid.uuid4())
        thread = NarrativeThread.objects.create(title="Update Thread")

        updated = get_or_create_chat_session(session.session_id, thread=thread)

        self.assertEqual(updated.id, session.id)
        self.assertEqual(updated.thread, thread)
        session.refresh_from_db()
        self.assertEqual(session.thread, thread)
