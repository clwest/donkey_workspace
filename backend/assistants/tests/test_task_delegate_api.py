import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, TaskAssignment


class TaskDelegateAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="del", password="pw")
        self.client.force_authenticate(self.user)
        self.sender = Assistant.objects.create(name="Sender", specialty="x")
        self.target = Assistant.objects.create(name="Target", specialty="y")
        self.url = f"/api/assistants/{self.sender.id}/delegate-task/"

    def test_delegate_creates_assignment(self):
        resp = self.client.post(
            self.url,
            {
                "task_description": "Do work",
                "target_assistant_id": str(self.target.id),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        assignment_id = resp.json()["assignment_id"]
        self.assertTrue(TaskAssignment.objects.filter(id=assignment_id).exists())
