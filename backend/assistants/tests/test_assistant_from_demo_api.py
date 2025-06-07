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
        resp = self.client.post(self.url, {"demo_slug": "prompt_pal", "transcript": transcript}, format="json")
        self.assertEqual(resp.status_code, 201)
        slug = resp.json()["slug"]
        self.assertTrue(Assistant.objects.filter(slug=slug, is_demo=False).exists())
        asst = Assistant.objects.get(slug=slug)
        self.assertEqual(asst.spawned_by, "demo:prompt_pal")
        self.assertGreater(asst.memories.count(), 0)
