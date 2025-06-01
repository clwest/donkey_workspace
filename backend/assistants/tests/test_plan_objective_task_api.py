from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import (
    Assistant,
    AssistantProject,
    AssistantObjective,
    AssistantTask,
)
from memory.models import MemoryEntry


class PlanObjectiveTaskAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Planner", specialty="test")
        self.memory = MemoryEntry.objects.create(
            event="Learn Django", assistant=self.assistant
        )

    def test_plan_objective_from_memory(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/plan-objective/"
        resp = self.client.post(url, {"memory_id": str(self.memory.id)}, format="json")
        self.assertEqual(resp.status_code, 201)
        obj = AssistantObjective.objects.first()
        self.assertEqual(obj.source_memory, self.memory)
        self.assertIsNotNone(obj.project)

    def test_plan_task_for_objective(self):
        project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        objective = AssistantObjective.objects.create(
            assistant=self.assistant, project=project, title="Goal"
        )
        url = f"/api/v1/assistants/{self.assistant.slug}/plan-task/"
        resp = self.client.post(url, {"objective_id": str(objective.id)}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AssistantTask.objects.filter(objective=objective).count(), 3)
