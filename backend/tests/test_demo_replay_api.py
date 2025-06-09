import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from unittest.mock import patch


class DemoReplayAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(assistant=self.assistant, session_id=self.session_id)

    @patch("assistants.views.demo.load_session_messages")
    @patch("assistants.views.demo.get_rag_chunk_debug")
    def test_replay_endpoint(self, mock_debug, mock_load):
        mock_load.return_value = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "a"},
            {"role": "user", "content": "bye"},
        ]
        mock_debug.return_value = {
            "matched_chunks": [],
            "fallback_chunks": [],
            "glossary_misses": [],
            "retrieval_score": 0.0,
            "glossary_scores": {},
            "fallback_triggered": False,
            "reason": None,
        }
        url = f"/api/assistants/{self.assistant.slug}/demo_replay/{self.session_id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["frames"]), 2)
