from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DelegationEvent, AssistantThoughtLog


class SubAgentReflectAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="p")
        self.child = Assistant.objects.create(name="Child", specialty="c")
        self.event = DelegationEvent.objects.create(
            parent_assistant=self.parent,
            child_assistant=self.child,
            reason="r",
        )
        AssistantThoughtLog.objects.create(
            assistant=self.child, thought="output", thought_type="generated"
        )

    def test_subagent_reflect(self):
        url = f"/api/v1/assistants/{self.parent.slug}/subagent_reflect/{self.event.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("summary", data)
