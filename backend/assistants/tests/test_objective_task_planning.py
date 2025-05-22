
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantProject, AssistantObjective, AssistantTask


class ObjectiveTaskPlanningAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="planner", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Planner", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        self.objective = AssistantObjective.objects.create(
            assistant=self.assistant, project=self.project, title="Launch"
        )

    def test_plan_tasks_for_objective(self):
        url = f"/api/assistants/{self.assistant.slug}/plan-tasks/{self.objective.id}/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(AssistantTask.objects.filter(objective=self.objective).count(), 3)

    def test_objectives_for_assistant(self):
        url = f"/api/assistants/{self.assistant.slug}/objectives/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        objs = resp.json()
        self.assertEqual(len(objs), 1)


