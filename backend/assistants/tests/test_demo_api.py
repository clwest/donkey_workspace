from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class DemoAssistantAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        Assistant.objects.create(name="Demo1", specialty="t", is_demo=True)
        Assistant.objects.create(name="Regular", specialty="x")
        self.url = "/api/v1/assistants/demos/"

    def test_list_demos(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Demo1")
        self.assertIn("demo_slug", data[0])
        demo = Assistant.objects.get(slug=data[0]["slug"])
        self.assertTrue(demo.memories.exists())
        self.assertTrue(all(m.is_demo for m in demo.memories.all()))

    def test_demo_protected(self):
        demo = Assistant.objects.filter(is_demo=True).first()
        resp = self.client.patch(
            f"/api/v1/assistants/{demo.slug}/",
            {"tone": "serious"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
        resp = self.client.delete(f"/api/v1/assistants/{demo.slug}/")
        self.assertEqual(resp.status_code, 403)

    def test_get_demo_assistants_endpoint(self):
        resp = self.client.get("/api/assistants/demos/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]["is_demo"])
