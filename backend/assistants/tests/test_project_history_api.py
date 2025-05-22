
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantProject, ProjectPlanningLog
from project.models import Project, ProjectTask


class ProjectHistoryAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="hist", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Hist", specialty="test")
        self.assistant_project = AssistantProject.objects.create(
            assistant=self.assistant, title="HP", created_by=self.user
        )
        self.project = Project.objects.create(
            user=self.user,
            title="Main",
            assistant=self.assistant,
            assistant_project=self.assistant_project,
        )
        ProjectTask.objects.create(project=self.project, title="Task", notes="", content="c")

    def test_history_endpoint(self):
        url = f"/api/v1/assistants/projects/{self.assistant_project.id}/history/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(len(data), 1)
