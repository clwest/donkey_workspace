
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class InsightPlanAPITest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Planner", specialty="p")
        self.url = f"/api/assistants/{self.assistant.id}/generate-plan/"

    def test_generate_plan(self):
        resp = self.client.post(self.url, {"context": "demo"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("plan", resp.json())
        self.assertIsInstance(resp.json()["plan"], list)
