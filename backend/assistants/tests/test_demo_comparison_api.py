from assistants.tests import BaseAPITestCase
from assistants.models import Assistant

class DemoComparisonAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        for i in range(3):
            Assistant.objects.create(name=f"Demo{i}", specialty="t", is_demo=True)
        self.url = "/api/assistants/demo_comparison/"

    def test_demo_comparison_returns_multiple(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(len(data), 2)
        item = data[0]
        self.assertIn("preview_chat", item)
        self.assertIn("traits", item)
        self.assertIn("motto", item)
        self.assertIn("tone", item)
        self.assertTrue(len(item["preview_chat"]) >= 1)
