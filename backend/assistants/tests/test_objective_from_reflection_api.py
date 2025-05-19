import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch
import uuid

from assistants.models import Assistant, AssistantProject, AssistantReflectionLog, AssistantObjective
from memory.models import MemoryEntry


class ObjectiveFromReflectionAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="api", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        self.project = AssistantProject.objects.create(assistant=self.assistant, title="P", created_by=self.user)
        self.mem = MemoryEntry.objects.create(event="m", assistant=self.assistant)
        self.reflection = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            linked_memory=self.mem,
            title="R",
            summary="sum",
        )

    @patch("assistants.utils.objective_from_reflection.complete_chat")
    def test_create_from_reflection(self, mock_chat):
        mock_chat.return_value = "Goal: Do it"
        url = f"/api/assistants/{self.assistant.slug}/objectives/from-reflection/"
        resp = self.client.post(url, {"reflection_id": str(self.reflection.id)}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AssistantObjective.objects.count(), 1)
        obj = AssistantObjective.objects.first()
        self.assertEqual(obj.generated_from_reflection, self.reflection)
        self.assertEqual(obj.source_memory, self.mem)

    def test_invalid_reflection(self):
        url = f"/api/assistants/{self.assistant.slug}/objectives/from-reflection/"
        resp = self.client.post(url, {"reflection_id": str(uuid.uuid4())}, format="json")
        self.assertEqual(resp.status_code, 404)

