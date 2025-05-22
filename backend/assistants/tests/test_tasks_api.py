
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from rest_framework import status
from assistants.models import Assistant, AssistantProject
from project.models import Project, ProjectTask


class ProjectTaskAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tasker", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Helper", specialty="test")
        self.assistant_project = AssistantProject.objects.create(
            assistant=self.assistant,
            title="Proj",
            created_by=self.user,
        )
        self.project = Project.objects.create(
            user=self.user,
            title="Core",
            assistant=self.assistant,
            assistant_project=self.assistant_project,
        )

    def test_create_task(self):
        url = f"/api/v1/assistants/projects/{self.assistant_project.id}/tasks/"
        payload = {
            "title": "Task 1",
            "notes": "Some notes",
            "status": "todo",
            "priority": 1,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjectTask.objects.filter(project=self.project).count(), 1)
