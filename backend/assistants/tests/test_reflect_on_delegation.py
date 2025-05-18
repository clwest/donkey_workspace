import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
import uuid
from unittest.mock import patch

from assistants.models import (
    Assistant,
    DelegationEvent,
    AssistantThoughtLog,
    ChatSession,
)
from assistants.tasks import reflect_on_delegation
from assistants.utils.delegation import spawn_delegated_assistant
from memory.models import MemoryEntry
from project.models import Project


class DelegationReflectionTaskTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="task", password="pw")
        self.parent = Assistant.objects.create(
            name="Parent", specialty="root", created_by=self.user
        )
        self.child = Assistant.objects.create(
            name="Child", specialty="helper", parent_assistant=self.parent
        )

    @patch("assistants.tasks.AssistantReflectionEngine.generate_reflection")
    def test_reflection_logged(self, mock_gen):
        mock_gen.return_value = "reflected"
        event = DelegationEvent.objects.create(
            parent_assistant=self.parent, child_assistant=self.child, reason="test"
        )

        reflect_on_delegation(event.id)

        log = AssistantThoughtLog.objects.filter(
            assistant=self.parent, category="reflection"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.thought, "reflected")


class DelegationSignalTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="sig", password="pw")
        self.parent = Assistant.objects.create(
            name="P", specialty="root", created_by=self.user
        )
        self.child = Assistant.objects.create(
            name="C", specialty="help", parent_assistant=self.parent
        )

    @patch("assistants.models.reflect_on_delegation.delay")
    def test_signal_triggers_task(self, mock_delay):
        event = DelegationEvent.objects.create(
            parent_assistant=self.parent, child_assistant=self.child, reason="auto"
        )
        mock_delay.assert_called_once_with(str(event.id))


class SpawnDelegationReflectionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="flow", password="pw")
        self.parent = Assistant.objects.create(
            name="P2", specialty="root", created_by=self.user
        )
        self.project = Project.objects.create(
            user=self.user, title="Proj", assistant=self.parent
        )
        self.session = ChatSession.objects.create(
            assistant=self.parent, project=self.project, session_id=uuid.uuid4()
        )
        self.memory = MemoryEntry.objects.create(
            event="Trig",
            assistant=self.parent,
            chat_session=self.session,
            related_project=self.project,
        )

    @patch("assistants.models.reflect_on_delegation.delay")
    @patch(
        "assistants.helpers.reflection_helpers.AssistantReflectionEngine.generate_reflection"
    )
    def test_spawn_creates_reflection(self, mock_gen, mock_delay):
        mock_gen.return_value = "auto"
        spawn_delegated_assistant(
            self.session,
            memory_entry=self.memory,
            name="Child",
            reason="test",
        )

        log = AssistantThoughtLog.objects.filter(
            assistant=self.parent, thought_type="reflection"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.thought, "auto")
        self.assertEqual(log.project, self.project)
        slugs = list(log.tags.values_list("slug", flat=True))
        self.assertIn("delegation", slugs)
        self.assertIn("auto-reflection", slugs)
