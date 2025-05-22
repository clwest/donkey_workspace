
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from rest_framework import status

from assistants.models import (
    Assistant,
    AssistantProject,
    AssistantObjective,
    AssistantTask,
    AssistantThoughtLog,
)


class RegenerateRecoveryPlanAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="rec", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(
            name="RecBot", specialty="x", needs_recovery=True
        )
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Plan", created_by=self.user
        )
        self.obj = AssistantObjective.objects.create(
            project=self.project, assistant=self.assistant, title="Goal"
        )
        AssistantTask.objects.create(
            project=self.project, objective=self.obj, title="Task"
        )

    def test_requires_recovery(self):
        self.assistant.needs_recovery = False
        self.assistant.save()
        url = f"/api/v1/assistants/{self.assistant.slug}/regenerate_plan/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_log_created(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/regenerate_plan/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AssistantThoughtLog.objects.filter(
                assistant=self.assistant, thought_type="regeneration"
            ).exists()
        )

    def test_approve_clears_flag(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/regenerate_plan/"
        resp = self.client.post(url, {"approve": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assistant.refresh_from_db()
        self.assertFalse(self.assistant.needs_recovery)
