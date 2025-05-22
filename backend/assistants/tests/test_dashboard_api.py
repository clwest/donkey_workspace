
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantThoughtLog, DelegationEvent, AssistantProject
from memory.models import MemoryEntry


class AssistantDashboardAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="dash", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Dash", specialty="dash")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant,
            title="Dash Project",
            created_by=self.user,
        )
        self.assistant.current_project = self.project
        self.assistant.save()
        other = Assistant.objects.create(name="Child", specialty="c")
        DelegationEvent.objects.create(
            parent_assistant=self.assistant,
            child_assistant=other,
            reason="r",
        )
        DelegationEvent.objects.create(
            parent_assistant=other,
            child_assistant=self.assistant,
            reason="r2",
        )
        for i in range(6):
            AssistantThoughtLog.objects.create(assistant=self.assistant, thought=f"t{i}")
            MemoryEntry.objects.create(event=f"m{i}", assistant=self.assistant)

    def test_dashboard_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/dashboard/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("assistant", data)
        self.assertIn("project", data)
        self.assertIn("thoughts", data)
        self.assertEqual(len(data["thoughts"]), 5)
        self.assertIn("recent_memories", data)
        self.assertEqual(len(data["recent_memories"]), 5)
        self.assertIn("delegations", data)
        self.assertEqual(len(data["delegations"]), 2)
        self.assertEqual(data["assistant"]["id"], str(self.assistant.id))
        self.assertEqual(data["project"]["id"], str(self.project.id))
