from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class AssistantFromDemoAPITest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.demo = Assistant.objects.create(
            name="Prompt Pal",
            specialty="demo",
            is_demo=True,
            demo_slug="prompt_pal",
            tone="friendly",
            primary_badge="starter",
            avatar="http://example.com/avatar.png",
        )
        self.url = "/api/assistants/from_demo/"

    def test_clone_demo_assistant(self):
        transcript = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]
        resp = self.client.post(
            self.url,
            {"demo_slug": "prompt_pal", "transcript": transcript},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        slug = resp.json()["slug"]
        self.assertEqual(resp.json()["demo_slug"], "prompt_pal")
        self.assertTrue(Assistant.objects.filter(slug=slug, is_demo=False).exists())
        asst = Assistant.objects.get(slug=slug)
        self.assertEqual(asst.spawn_reason, "demo:prompt_pal")
        self.assertEqual(asst.spawned_by, self.demo)
        self.assertListEqual(asst.spawned_traits, ["badge", "tone", "avatar"])
        self.assertTrue(asst.is_demo_clone)
        self.assertGreater(asst.memories.count(), 0)

    def test_clone_with_retain_prompt(self):
        transcript = [{"role": "user", "content": "Hi"}]
        resp = self.client.post(
            self.url,
            {
                "demo_slug": "prompt_pal",
                "transcript": transcript,
                "retain_starter_prompt": True,
                "demo_session_id": "s1",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        slug = resp.json()["slug"]
        asst = Assistant.objects.get(slug=slug)
        self.assertIsNotNone(asst.system_prompt)
        self.assertIn("Boosted from demo session", asst.prompt_notes)

    def test_clone_without_retain_prompt(self):
        resp = self.client.post(
            self.url,
            {
                "demo_slug": "prompt_pal",
                "transcript": [],
                "retain_starter_prompt": False,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        slug = resp.json()["slug"]
        asst = Assistant.objects.get(slug=slug)
        self.assertIsNone(asst.system_prompt)

    def test_clone_with_boost(self):
        transcript = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"},
        ]
        resp = self.client.post(
            self.url,
            {
                "demo_slug": "prompt_pal",
                "transcript": transcript,
                "demo_session_id": "s1",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        slug = resp.json()["slug"]
        self.assertIsNotNone(resp.json().get("boost_summary"))
        asst = Assistant.objects.get(slug=slug)
        self.assertTrue(asst.boosted_from_demo)
        self.assertTrue(asst.prompt_notes)
