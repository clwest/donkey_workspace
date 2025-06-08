from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DemoUsageLog
from assistants.helpers.demo_utils import generate_assistant_from_demo


class DemoBoostAPITest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.demo = Assistant.objects.create(
            name="Demo",
            slug="demo",
            is_demo=True,
            demo_slug="demo",
        )
        self.url = "/api/assistants/demo_boost/"
        DemoUsageLog.objects.create(assistant=self.demo, session_id="d1")

    def test_replay_demo_boost(self):
        resp = self.client.post(self.url, {"demo_session_id": "d1"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("slug", data)
        slug = data["slug"]
        asst = Assistant.objects.get(slug=slug)
        self.assertTrue(asst.boosted_from_demo)
