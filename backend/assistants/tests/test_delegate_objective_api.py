
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import (
    Assistant,
    AssistantProject,
    AssistantObjective,
    DelegationEvent,
)


class DelegateObjectiveAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="obj", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Parent", specialty="root")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        self.objective = AssistantObjective.objects.create(
            project=self.project,
            assistant=self.assistant,
            title="Research",
            description="test",
        )

    def test_delegate_from_objective(self):
        url = f"/api/assistants/{self.assistant.slug}/delegate/{self.objective.id}/"
        resp = self.client.post(url, {}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(DelegationEvent.objects.count(), 1)
        child = Assistant.objects.filter(parent_assistant=self.assistant).first()
        self.assertIsNotNone(child)
        event = DelegationEvent.objects.first()
        self.assertEqual(event.objective_id, self.objective.id)
        self.objective.refresh_from_db()
        self.assertEqual(self.objective.delegated_assistant_id, child.id)
