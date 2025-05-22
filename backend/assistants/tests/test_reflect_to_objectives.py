
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from unittest.mock import patch

from assistants.models import Assistant, AssistantProject, AssistantThoughtLog, AssistantObjective

class ReflectToObjectivesAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="objgen", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Planner", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        for i in range(3):
            AssistantThoughtLog.objects.create(
                assistant=self.assistant,
                project=self.project,
                thought=f"Idea {i}",
                thought_type="generated",
            )

    @patch("assistants.views.objectives.complete_chat")
    def test_reflect_to_objectives(self, mock_chat):
        mock_chat.return_value = "- Goal One: Desc\n- Goal Two"
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect-to-objectives/"
        resp = self.client.post(url, {"project_id": str(self.project.id)}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(AssistantObjective.objects.filter(project=self.project).count(), 2)
