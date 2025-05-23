import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from workflows.models import WorkflowDefinition, WorkflowExecutionLog
from assistants.models import Assistant


class WorkflowExecuteAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.defn = WorkflowDefinition.objects.create(
            name="wf",
            step_sequence=[],
            mythic_rationale="r",
            created_by=self.assistant,
        )

    def test_execute_endpoint(self):
        resp = self.client.post(
            "/api/workflows/execute/",
            {
                "workflow_definition_id": self.defn.id,
                "triggered_by_id": self.assistant.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(
            WorkflowExecutionLog.objects.filter(id=data["execution_id"]).exists()
        )
