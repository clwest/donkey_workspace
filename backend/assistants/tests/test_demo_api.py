from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DemoUsageLog


class DemoAssistantAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.demo1 = Assistant.objects.create(name="Demo1", specialty="t", is_demo=True)
        self.demo2 = Assistant.objects.create(name="Demo2", specialty="t", is_demo=True)
        self.demo3 = Assistant.objects.create(name="Demo3", specialty="t", is_demo=True)
        Assistant.objects.create(name="Regular", specialty="x")
        DemoUsageLog.objects.create(assistant=self.demo1, session_id="s1", converted_to_real_assistant=True)
        DemoUsageLog.objects.create(assistant=self.demo1, session_id="s2")
        DemoUsageLog.objects.create(assistant=self.demo2, session_id="s3", converted_to_real_assistant=True)
        DemoUsageLog.objects.create(assistant=self.demo2, session_id="s4", converted_to_real_assistant=True)
        DemoUsageLog.objects.create(assistant=self.demo2, session_id="s5")
        DemoUsageLog.objects.create(assistant=self.demo3, session_id="s6")
        self.url = "/api/v1/assistants/demos/"

    def test_list_demos(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        slugs = [d["slug"] for d in data]
        self.assertIn(self.demo1.slug, slugs)
        demo = Assistant.objects.get(slug=self.demo1.slug)
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
        self.assertEqual(len(data), 3)
        self.assertTrue(all(d["is_demo"] for d in data))
        self.assertIn("metrics", data[0])
        self.assertIn("is_featured", data[0])

    def test_demo_usage_overview_endpoint(self):
        resp = self.client.get("/api/assistants/demo_usage/overview/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_sessions", data)
        self.assertIn("conversion_rate", data)

    def test_demo_leaderboard_endpoint(self):
        demo = Assistant.objects.filter(is_demo=True).first()
        from assistants.models.demo_usage import DemoSessionLog
        DemoSessionLog.objects.create(
            assistant=demo,
            session_id="s1",
            message_count=2,
            demo_interaction_score=5,
            converted_to_real_assistant=True,
        )
        DemoSessionLog.objects.create(
            assistant=demo,
            session_id="s2",
            message_count=1,
            demo_interaction_score=3,
        )
        resp = self.client.get("/api/assistants/demo_leaderboard/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        row = data[0]
        self.assertIn("demo_slug", row)
        self.assertIn("conversion_rate", row)
