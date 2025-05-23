import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from workflows.models import WorkflowDefinition
from assistants.models import Assistant


class WorkflowDefinitionAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")

    def test_create_and_list(self):
        resp = self.client.post(
            "/api/workflows/definitions/",
            {
                "name": "wf1",
                "step_sequence": [],
                "mythic_rationale": "r",
                "created_by": self.assistant.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/workflows/definitions/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.json()), 1)
