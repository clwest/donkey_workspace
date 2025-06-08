from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.utils.session_utils import save_message_to_session


class PrepareCreationFromDemoAPITest(BaseAPITestCase):
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
        self.url = f"/api/assistants/{self.demo.slug}/prepare_creation_from_demo/"
        self.session_id = "demo_test"
        save_message_to_session(self.session_id, "user", "Hi")
        save_message_to_session(self.session_id, "assistant", "Hello")

    def test_preview_endpoint_returns_data(self):
        resp = self.client.post(
            self.url, {"transcript": [{"role": "user", "content": "Hi"}]}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant"]["name"], "Prompt Pal")
        self.assertIn("suggested_system_prompt", data)
        self.assertIsInstance(data["recent_messages"], list)
        self.assertIn("boost_summary", data)
        self.assertIn("origin_traits", data)
