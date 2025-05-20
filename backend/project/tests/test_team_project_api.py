import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantMemoryChain
from memory.models import MemoryEntry
from project.models import Project
from assistants.helpers.team_memory import propagate_memory_to_team_chain


class ProjectTeamAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="team", password="pw")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(user=self.user, title="TeamProj")
        self.assistant = Assistant.objects.create(name="Robo", specialty="t")
        self.chain = AssistantMemoryChain.objects.create(
            title="TeamChain",
            project=self.project,
            linked_project=self.project,
            is_team_chain=True,
        )
        self.project.team_chain = self.chain
        self.project.save()

    def test_assign_role_endpoint(self):
        url = f"/api/projects/{self.project.id}/assign_role/"
        resp = self.client.post(
            url,
            {"assistant_id": str(self.assistant.id), "role": "researcher"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.project.refresh_from_db()
        self.assertIn(str(self.assistant.id), self.project.roles)

    def test_propagate_memory_adds_to_chain(self):
        mem = MemoryEntry.objects.create(
            event="hi", assistant=self.assistant, related_project=self.project
        )
        propagate_memory_to_team_chain(mem)
        self.assertIn(mem, self.chain.memories.all())
