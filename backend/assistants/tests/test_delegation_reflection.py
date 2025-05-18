import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase

from assistants.models import Assistant, AssistantProject, AssistantThoughtLog
from mcp_core.models import NarrativeThread
from assistants.utils.delegation import spawn_delegated_assistant
from assistants.tasks import reflect_on_spawned_assistant
from project.models import Project
from assistants.models import ChatSession


class DelegatedAssistantReflectionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="zeno", password="pw")
        self.parent = Assistant.objects.create(
            name="Parent", specialty="root", created_by=self.user
        )
        self.project = AssistantProject.objects.create(
            assistant=self.parent,
            title="Proj",
            created_by=self.user,
        )
        self.thread = NarrativeThread.objects.create(
            title="Delegation", created_by=self.user
        )

    def test_reflection_logged_after_spawn(self):
        child = spawn_delegated_assistant(
            self.parent,
            self.project,
            name="Child",
            description="test",
            specialty="helper",
            narrative_thread=self.thread,
        )
        child_project = Project.objects.filter(assistant=child).first()
        session = ChatSession.objects.filter(assistant=child).first()
        # execute queued reflection synchronously
        reflect_on_spawned_assistant(
            self.parent.id,
            child.id,
            self.project.id,
            self.thread.id,
        )
        log = AssistantThoughtLog.objects.filter(
            assistant=self.parent, thought_type="reflection"
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.narrative_thread_id, self.thread.id)
        self.assertEqual(child_project.narrative_thread_id, self.thread.id)
        self.assertEqual(session.narrative_thread_id, self.thread.id)
        self.assertEqual(child_project.thread_id, self.thread.id)
        self.assertEqual(session.thread_id, self.thread.id)
