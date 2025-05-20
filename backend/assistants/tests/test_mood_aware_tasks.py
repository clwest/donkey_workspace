import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from assistants.models import (
    Assistant,
    AssistantProject,
    AssistantObjective,
    ChatSession,
    StructuredMemory,
    AssistantTask,
)
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine


class MoodAwareTaskTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="mood", password="pw")
        self.assistant = Assistant.objects.create(name="Mooder", specialty="t")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="P", created_by=self.user
        )
        self.objective = AssistantObjective.objects.create(
            project=self.project, assistant=self.assistant, title="Obj"
        )
        self.session = ChatSession.objects.create(
            assistant=self.assistant, project=self.project
        )
        StructuredMemory.objects.create(
            user=self.user,
            session=self.session,
            memory_key="mood",
            memory_value="playful",
        )

    def test_task_tone_from_session_mood(self):
        engine = AssistantThoughtEngine(assistant=self.assistant, project=self.project)
        tasks = engine.plan_tasks_from_objective(self.objective)
        self.assertTrue(all(t.tone == "playful" for t in tasks))
        self.assertTrue(all(t.generated_from_mood == "playful" for t in tasks))
