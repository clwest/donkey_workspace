import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from unittest.mock import patch

from agents.models.core import Agent, KnowledgeGrowthLog
from django.contrib.auth import get_user_model
from intel_core.models import Document, DocumentChunk
from rest_framework.test import APITestCase


class UploadKnowledgeAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="k", password="pw")
        self.client.force_authenticate(user=self.user)
        self.agent = Agent.objects.create(name="A", slug="a")

    @patch("agents.views.agents.call_llm")
    @patch("agents.views.agents.DocumentService.ingest")
    def test_upload_url(self, mock_ingest, mock_llm):
        doc = Document.objects.create(title="d", content="c", source_type="url")
        DocumentChunk.objects.create(
            document=doc, order=0, text="t", tokens=1, fingerprint="f"
        )
        mock_ingest.return_value = [{"document_id": str(doc.id), "embedded_chunks": 1, "total_chunks": 1, "summary": ""}]
        mock_llm.return_value = "- s"
        resp = self.client.post(
            f"/api/v1/agents/{self.agent.id}/upload_knowledge/",
            {"url": "http://x.com"},
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(KnowledgeGrowthLog.objects.count(), 1)

    @patch("agents.views.agents.call_llm")
    @patch("agents.views.agents.DocumentService.ingest_text")
    def test_upload_raw_text(self, mock_ingest, mock_llm):
        doc = Document.objects.create(title="d2", content="c2", source_type="text")
        DocumentChunk.objects.create(
            document=doc, order=0, text="t", tokens=1, fingerprint="f2"
        )
        mock_ingest.return_value = [{"document_id": str(doc.id), "embedded_chunks": 1, "total_chunks": 1, "summary": ""}]
        mock_llm.return_value = "- b"
        resp = self.client.post(
            f"/api/v1/agents/{self.agent.id}/upload_knowledge/",
            {"raw_text": "hello"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(KnowledgeGrowthLog.objects.count(), 1)

    def test_invalid_input(self):
        resp = self.client.post(f"/api/v1/agents/{self.agent.id}/upload_knowledge/", {})
        self.assertEqual(resp.status_code, 400)
