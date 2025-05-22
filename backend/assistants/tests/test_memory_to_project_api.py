
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantProject, AssistantObjective, AssistantTask
from memory.models import MemoryEntry
from project.models import Project, ProjectMemoryLink


class MemoryToProjectAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="planner", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Planner", specialty="test")
        self.mem1 = MemoryEntry.objects.create(event="First memory", assistant=self.assistant, summary="One")
        self.mem2 = MemoryEntry.objects.create(event="Second memory", assistant=self.assistant, summary="Two")

    def test_plan_project_from_memory(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/memory-to-project/"
        resp = self.client.post(
            url,
            {
                "memory_ids": [str(self.mem1.id), str(self.mem2.id)],
                "planning_style": "bullet",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("project_id", data)
        project = AssistantProject.objects.get(id=data["project_id"])
        self.assertEqual(project.objectives.count(), 2)
        self.assertEqual(project.tasks.count(), 2)
        core_project = Project.objects.get(assistant_project=project)
        self.assertEqual(ProjectMemoryLink.objects.filter(project=core_project).count(), 2)
