import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from assistants.models import AssistantMemoryChain
from project.models import Project


class ProjectMemoryPermissionTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.project = Project.objects.create(user=self.owner, title="MemProj")
        self.chain = AssistantMemoryChain.objects.create(
            title="TeamChain",
            project=self.project,
            linked_project=self.project,
            is_team_chain=True,
        )
        self.project.team_chain = self.chain
        self.project.save()

    def test_owner_can_access_team_memory(self):
        self.client.force_authenticate(user=self.owner)
        url = f"/api/v1/projects/{self.project.id}/team_memory/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_other_user_forbidden(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/v1/projects/{self.project.id}/team_memory/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
