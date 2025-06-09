import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from unittest.mock import patch


class DemoReflectionComposeAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(assistant=self.assistant, session_id=self.session_id)

    @patch("assistants.helpers.demo_utils.get_rag_chunk_debug")
    @patch("assistants.helpers.demo_utils.load_session_messages")
    def test_compose(self, mock_load, mock_debug):
        mock_load.return_value = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "what is mcp"},
        ]
        mock_debug.return_value = {
            "matched_chunks": [{"anchor_slug": "mcp"}],
            "fallback_chunks": [],
            "glossary_misses": [],
            "retrieval_score": 0.0,
            "glossary_scores": {},
            "fallback_triggered": False,
            "reason": None,
        }
        url = f"/api/assistants/{self.assistant.slug}/demo_reflection/compose/"
        resp = self.client.post(url, {"session_id": self.session_id}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("summary", resp.data)
        self.assertEqual(resp.data["anchors_used"], ["mcp"])
