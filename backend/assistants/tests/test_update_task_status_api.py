
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from project.models import Project, ProjectTask
from assistants.models import Assistant, AssistantProject


class UpdateTaskStatusAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tasker", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="U", specialty="t")
        self.assist_proj = AssistantProject.objects.create(
            assistant=self.assistant, title="P", created_by=self.user
        )
        self.project = Project.objects.create(
            user=self.user,
            title="Core",
            assistant=self.assistant,
            assistant_project=self.assist_proj,
        )
        self.task = ProjectTask.objects.create(
            project=self.project,
            title="T",
            status="new",
            content="do",
        )

    def test_update_status(self):
        url = f"/api/v1/assistants/tasks/{self.task.id}/update_status/"
        resp = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")
