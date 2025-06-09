import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from memory.models import RAGPlaybackLog


class DriftRefinementAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(assistant=self.assistant, session_id=self.session_id)
        RAGPlaybackLog.objects.create(
            assistant=self.assistant,
            query="foo",
            query_term="foo",
            memory_context=None,
            chunks=[{"id": "c1", "is_fallback": True, "anchor_match": False}],
            demo_session_id=self.session_id,
        )
        RAGPlaybackLog.objects.create(
            assistant=self.assistant,
            query="foo",
            query_term="foo",
            memory_context=None,
            chunks=[{"id": "c2", "is_fallback": True, "anchor_match": False}],
            demo_session_id=self.session_id,
        )

    def test_glossary_dedupe(self):
        url = f"/api/assistants/{self.assistant.slug}/refine_from_drift/"
        resp = self.client.post(url, {"session_id": self.session_id}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["glossary_fixes"], [{"term": "foo", "cause": "fallback"}])
