
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantProject, AssistantObjective
from memory.models import MemoryEntry
from project.models import Project, ProjectMemoryLink


class CreateProjectFromMemoryAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="creator", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(
            name="Helper", specialty="test", created_by=self.user
        )
        self.memory = MemoryEntry.objects.create(
            event="Remember", assistant=self.assistant, summary="Sum"
        )

    def test_create_project_from_memory(self):
        url = "/api/v1/assistants/projects/from-memory/"
        resp = self.client.post(
            url,
            {
                "assistant_id": str(self.assistant.id),
                "memory_id": str(self.memory.id),
                "title": "Memory Project",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("project_id", data)
        project = AssistantProject.objects.get(id=data["project_id"])
        self.assertEqual(project.assistant, self.assistant)
        core_project = Project.objects.get(assistant_project=project)
        self.assertEqual(core_project.created_from_memory, self.memory)
        self.assertTrue(
            ProjectMemoryLink.objects.filter(
                project=core_project, memory=self.memory
            ).exists()
        )
        self.assertEqual(project.objectives.count(), 1)
        obj = project.objectives.first()
        self.assertEqual(obj.source_memory, self.memory)

    def test_create_project_from_memory_by_slug(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/projects/from-memory/"
        resp = self.client.post(
            url,
            {"memory_id": str(self.memory.id)},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        project = AssistantProject.objects.get(id=data["project_id"])
        self.assertEqual(project.assistant, self.assistant)
        core_project = Project.objects.get(assistant_project=project)
        self.assertEqual(core_project.created_from_memory, self.memory)
        self.assertTrue(
            ProjectMemoryLink.objects.filter(
                project=core_project, memory=self.memory
            ).exists()
        )
        obj = project.objectives.first()
        self.assertEqual(obj.source_memory, self.memory)

    def test_create_project_from_memory_idempotent(self):
        url = "/api/v1/assistants/projects/from-memory/"
        data = {
            "assistant_id": str(self.assistant.id),
            "memory_id": str(self.memory.id),
            "title": "Memory Project",
        }
        resp1 = self.client.post(url, data, format="json")
        self.assertEqual(resp1.status_code, 201)
        resp2 = self.client.post(url, data, format="json")
        self.assertEqual(resp2.status_code, 201)
        self.assertEqual(
            AssistantProject.objects.filter(
                assistant=self.assistant, title="Memory Project"
            ).count(),
            1,
        )
