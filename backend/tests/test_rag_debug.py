import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from assistants.models import Assistant
from memory.models import RAGGroundingLog, GlossaryChangeEvent

class RagDebugTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.client = APIClient()

    def test_recent_log_endpoint(self):
        log = RAGGroundingLog.objects.create(
            assistant=self.assistant,
            query="q1",
            used_chunk_ids=["1"],
            retrieval_score=0.5,
            boosted_from_reflection=False,
            reflection_boost_score=0.0,
            glossary_boost_type="chunk",
        )
        old = RAGGroundingLog.objects.create(
            assistant=self.assistant,
            query="old",
            used_chunk_ids=["2"],
            retrieval_score=0.1,
            boosted_from_reflection=False,
            reflection_boost_score=0.0,
            glossary_boost_type="chunk",
        )
        old.created_at = timezone.now() - timedelta(days=2)
        old.save(update_fields=["created_at"])

        resp = self.client.get(f"/api/assistants/{self.assistant.slug}/rag_debug/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["query"], "q1")

    def test_boost_anchors_endpoint(self):
        resp = self.client.post(
            f"/api/assistants/{self.assistant.slug}/boost_anchors/",
            {"terms": ["zk rollup"], "boost": 0.2},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(GlossaryChangeEvent.objects.filter(term="zk rollup").count(), 1)

    def test_suggest_glossary_anchor_endpoint(self):
        resp = self.client.post(
            f"/api/assistants/{self.assistant.slug}/suggest_glossary_anchor/",
            {"term": "zk rollup"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(GlossaryChangeEvent.objects.filter(term="zk rollup").count(), 1)

    @patch("utils.llm_router.chat")
    def test_fallback_log_created_without_debug(self, mock_chat):
        mock_chat.return_value = (
            "fallback",
            [],
            {
                "used_chunks": [],
                "rag_fallback": True,
                "retrieval_score": 0.0,
                "anchor_hits": [],
                "anchor_misses": [],
                "fallback_reason": "no_chunks",
            },
        )
        resp = self.client.post(
            f"/api/v1/assistants/{self.assistant.slug}/chat/",
            {"message": "hi", "session_id": "s1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        log = RAGGroundingLog.objects.filter(assistant=self.assistant).first()
        self.assertIsNotNone(log)
        self.assertTrue(log.fallback_triggered)
        self.assertEqual(log.fallback_reason, "no_chunks")
