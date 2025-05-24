import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from unittest.mock import patch

from intel_core.models import Document, DocumentSet
from assistants.models import Assistant, AssistantThoughtLog


class BootstrapAssistantViewTest(APITestCase):
    def setUp(self):
        self.doc = Document.objects.create(
            title="MCP Docs",
            content="Some content",
            source_url="http://example.com",
        )
        self.doc_set = DocumentSet.objects.create(title="MCP Docs", urls=[], videos=[], tags=[])
        self.doc_set.pdf_files.add(self.doc)
        self.url = f"/api/v1/intel/document-sets/{self.doc_set.id}/bootstrap-assistant/"

    def _fake_completion(self):
        class Msg:
            content = (
                '{"name": "MCP Helper", "system_prompt": "Help", "tone": "neutral", '
                '"personality": "cheery", "specialties": ["mcp"]}'
            )

        class Choice:
            message = Msg()

        class Resp:
            choices = [Choice()]

        return Resp()

    @patch("intel_core.views.intelligence.client.chat.completions.create")
    def test_reuse_existing_assistant(self, mock_create):
        mock_create.return_value = self._fake_completion()
        resp1 = self.client.post(self.url)
        self.assertEqual(resp1.status_code, 200)
        slug = resp1.data["slug"]
        self.assertEqual(Assistant.objects.count(), 1)
        self.assertEqual(
            AssistantThoughtLog.objects.filter(assistant__slug=slug).count(), 1
        )

        mock_create.return_value = self._fake_completion()
        resp2 = self.client.post(self.url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Assistant.objects.count(), 1)
        self.assertEqual(resp2.data["slug"], slug)

    @patch("intel_core.views.intelligence.client.chat.completions.create")
    def test_detail_includes_document_info(self, mock_create):
        mock_create.return_value = self._fake_completion()
        resp = self.client.post(self.url)
        slug = resp.data["slug"]

        detail = self.client.get(f"/api/v1/assistants/{slug}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["source_document_title"], self.doc.title)
        self.assertEqual(detail.data["source_document_url"], self.doc.source_url)
