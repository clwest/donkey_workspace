import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, CollaborationLog, AssistantProjectRole
from project.models import Project


class CollaborationAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="col", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(
            name="A1",
            specialty="x",
            created_by=self.user,
            collaboration_style="harmonizer",
        )
        self.a2 = Assistant.objects.create(
            name="A2",
            specialty="x",
            created_by=self.user,
            collaboration_style="challenger",
        )
        self.project = Project.objects.create(title="P")
        AssistantProjectRole.objects.create(
            assistant=self.a1, project=self.project, role_name="lead"
        )
        AssistantProjectRole.objects.create(
            assistant=self.a2, project=self.project, role_name="support"
        )

    def test_evaluate_collaboration_creates_log(self):
        url = f"/api/assistants/{self.a1.slug}/evaluate-collaboration/"
        resp = self.client.post(
            url, {"project_id": str(self.project.id)}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data["style_conflict_detected"])
        logs_url = f"/api/projects/{self.project.id}/collaboration_logs/"
        logs = self.client.get(logs_url).json()
        self.assertEqual(len(logs), 1)
        self.assertEqual(CollaborationLog.objects.count(), 1)
