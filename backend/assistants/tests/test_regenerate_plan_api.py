import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantProject, ProjectPlanningLog
from memory.models import MemoryEntry


class RegeneratePlanAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="api", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Api", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="APIProj", created_by=self.user
        )
        MemoryEntry.objects.create(
            event="Shift", importance=9, assistant=self.assistant
        )

    def test_regenerate_endpoint(self):
        url = f"/api/assistants/projects/{self.project.id}/regenerate-plan/"
        resp = self.client.post(url, {"reason": "feedback"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            ProjectPlanningLog.objects.filter(
                project=self.project, event_type="plan_regenerated"
            ).exists()
        )

    def test_memory_changes_endpoint(self):
        url = f"/api/assistants/projects/{self.project.id}/memory-changes/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
