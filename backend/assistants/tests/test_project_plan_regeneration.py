import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import (
    Assistant,
    AssistantProject,
    ProjectPlanningLog,
    AssistantThoughtLog,
)
from memory.models import MemoryEntry


class ProjectPlanRegenerationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="replan", password="pw")
        self.assistant = Assistant.objects.create(name="R", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="RProj", created_by=self.user
        )
        for i in range(3):
            MemoryEntry.objects.create(
                event=f"Important {i}", importance=9, assistant=self.assistant
            )

    def test_regeneration_creates_logs(self):
        self.project.regenerate_project_plan_from_memory(reason="memory_shift")
        self.assertTrue(
            ProjectPlanningLog.objects.filter(
                project=self.project, event_type="plan_regenerated"
            ).exists()
        )
        thought = AssistantThoughtLog.objects.filter(
            project=self.project, event="project_plan_revised"
        ).first()
        self.assertIsNotNone(thought)
        self.assertEqual(thought.source_reason, "memory_shift")
