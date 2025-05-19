import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from assistants.models import Assistant, AssistantProject

class AssignProjectAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="assigner", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A1", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant,
            title="Project X",
            created_by=self.user,
        )

    def test_assign_project(self):
        url = f"/api/assistants/{self.assistant.slug}/assign_project/"
        resp = self.client.post(url, {"project_id": str(self.project.id)}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.current_project, self.project)

        detail = self.client.get(f"/api/assistants/{self.assistant.slug}/")
        self.assertEqual(detail.status_code, 200)
        data = detail.json()
        self.assertIn("current_project", data)
        self.assertEqual(data["current_project"]["id"], str(self.project.id))
