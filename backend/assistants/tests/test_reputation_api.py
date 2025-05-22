from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantReputation


class ReputationAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="RepGuy")

    def test_reputation_endpoint(self):
        url = f"/api/assistants/{self.assistant.slug}/reputation/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant"], self.assistant.id)
        self.assertIn("reputation_score", data)
