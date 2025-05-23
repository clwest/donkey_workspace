from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantProject, AssistantObjective


class PrimaryObjectivesAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.primary = Assistant.objects.create(
            name="Boss", specialty="manage", is_primary=True
        )
        self.project = AssistantProject.objects.create(
            assistant=self.primary, title="Main", created_by=self.user
        )
        self.obj = AssistantObjective.objects.create(
            assistant=self.primary, project=self.project, title="Test"
        )

    def test_primary_objectives(self):
        url = "/api/v1/assistants/primary/objectives/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test")
