import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from unittest.mock import patch
from assistants.models import Assistant, AssistantProject, AssistantReflectionLog, AssistantObjective, AssistantThoughtLog
from assistants.utils.objective_from_reflection import generate_objective_from_reflection
from memory.models import MemoryEntry
from django.test import TestCase


class GenerateObjectiveFromReflectionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="obj", password="pw")
        self.assistant = Assistant.objects.create(name="A", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        self.memory = MemoryEntry.objects.create(event="m1", assistant=self.assistant)
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            linked_memory=self.memory,
            title="R",
            summary="We learned things",
        )

    @patch("assistants.utils.objective_from_reflection.complete_chat")
    def test_generate(self, mock_chat):
        mock_chat.return_value = "Launch App: Build and deploy"
        obj = generate_objective_from_reflection(self.reflection)
        self.assertIsInstance(obj, AssistantObjective)
        self.assertEqual(obj.generated_from_reflection, self.reflection)
        self.assertEqual(obj.source_memory, self.memory)
        self.assertEqual(AssistantThoughtLog.objects.filter(thought="objective evolved").count(), 1)
