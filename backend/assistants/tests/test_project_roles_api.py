
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from rest_framework import status

from assistants.models import Assistant, AssistantProject


class ProjectRolesAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="roles", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="core")
        self.a2 = Assistant.objects.create(name="A2", specialty="helper")
        self.project = AssistantProject.objects.create(
            assistant=self.a1, title="RProject", created_by=self.user
        )

    def test_create_role_without_project_field(self):
        url = f"/api/assistants/projects/{self.project.id}/roles/"
        payload = {"assistant": self.a2.id, "role_name": "support"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["assistant"], str(self.a2.id))
        self.assertEqual(resp.data["role_name"], "support")

        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(len(resp_get.data), 1)


