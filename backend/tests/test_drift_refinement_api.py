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

    def test_summary_recent_refinements(self):
        from assistants.models.assistant import AssistantDriftRefinementLog

        AssistantDriftRefinementLog.objects.create(
            assistant=self.assistant,
            glossary_terms=["foo"],
            prompt_sections=["intro"],
            tone_tags=["friendly"],
        )
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/summary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("recent_refinements", data)
        self.assertEqual(data["recent_refinements"]["glossary"], ["foo"])

    def test_drift_fixes_sorted(self):
        from assistants.models.assistant import AssistantDriftRefinementLog
        log1 = AssistantDriftRefinementLog.objects.create(
            assistant=self.assistant,
            glossary_terms=["a"],
        )
        log2 = AssistantDriftRefinementLog.objects.create(
            assistant=self.assistant,
            glossary_terms=["b"],
        )
        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/drift_fixes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(str(log2.id), data[0]["id"])

    def test_drift_fixes_empty(self):
        assistant = Assistant.objects.create(name="B", slug="b")
        resp = self.client.get(f"/api/assistants/{assistant.slug}/drift_fixes/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["detail"], "no refinement logs found")
