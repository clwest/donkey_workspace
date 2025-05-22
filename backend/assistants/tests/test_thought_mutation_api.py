
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantThoughtLog


class ThoughtMutationAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.thought = AssistantThoughtLog.objects.create(
            assistant=self.assistant,
            thought="Original thought",
            feedback="unclear",
        )

    def test_mutate_thought_endpoint(self):
        url = f"/api/v1/assistants/thoughts/{self.thought.id}/mutate/"
        resp = self.client.post(url, {"style": "clarify"}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["parent_thought"], str(self.thought.id))
        self.assertEqual(data["thought_type"], "mutation")
        self.assertTrue(AssistantThoughtLog.objects.filter(parent_thought=self.thought).exists())
