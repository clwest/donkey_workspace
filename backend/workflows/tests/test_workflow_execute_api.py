import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from workflows.models import WorkflowDefinition, WorkflowExecutionLog


class WorkflowExecuteAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.defn = WorkflowDefinition.objects.create(name="wf", steps=[]) 

    def test_execute_endpoint(self):
        resp = self.client.post(
            "/api/v1/workflows/execute/",
            {"workflow_definition_id": self.defn.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(WorkflowExecutionLog.objects.filter(id=data["execution_id"]).exists())
