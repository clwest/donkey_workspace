import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, AssistantProject, AssistantThoughtLog, AssistantReflectionLog
from memory.models import MemoryEntry
from assistants.helpers.logging_helper import log_assistant_thought

class ThoughtMemoryReflectionTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="p")
        self.assistant = Assistant.objects.create(name="A", specialty="s", created_by=self.user)
        self.project = AssistantProject.objects.create(assistant=self.assistant, title="P", created_by=self.user)
        self.memory = MemoryEntry.objects.create(event="m", assistant=self.assistant)
        self.reflection = AssistantReflectionLog.objects.create(assistant=self.assistant, project=self.project, title="R", summary="sum")

    def test_log_links_memory_and_reflection(self):
        log = log_assistant_thought(
            self.assistant,
            "think",
            linked_memory=self.memory,
            linked_memories=[self.memory],
            linked_reflection=self.reflection,
            project=self.project,
            thought_type="reflection",
        )
        self.assertEqual(log.linked_memory, self.memory)
        self.assertIn(self.memory, log.linked_memories.all())
        self.assertEqual(log.linked_reflection, self.reflection)

    def test_reflection_thoughts_endpoint(self):
        log = AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            thought="t",
            thought_type="reflection",
            linked_reflection=self.reflection,
        )
        resp = self.client.get(f"/api/assistants/reflections/{self.reflection.id}/thoughts/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], str(log.id))
