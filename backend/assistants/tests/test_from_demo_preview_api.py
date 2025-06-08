from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class FromDemoPreviewAPITest(BaseAPITestCase):
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
        self.url = "/api/assistants/from_demo/preview/"

    def test_preview_returns_boost_and_traits(self):
        resp = self.client.post(
            self.url,
            {
                "demo_slug": "prompt_pal",
                "transcript": [{"role": "user", "content": "Hi"}],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("boost_summary", data)
        self.assertIn("origin_traits", data)
