import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from memory.models import RAGPlaybackLog


class DemoRAGOverlayAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(assistant=self.assistant, session_id=self.session_id)
        RAGPlaybackLog.objects.create(
            assistant=self.assistant,
            query="hi",
            memory_context=None,
            chunks=[{"id": "c1", "is_fallback": False, "anchor_match": True, "glossary_score": 0.5}],
            demo_session_id=self.session_id,
        )

    def test_overlay(self):
        url = f"/api/assistants/{self.assistant.slug}/demo_session/{self.session_id}/rag_overlay/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertIn("chunks", data[0])
