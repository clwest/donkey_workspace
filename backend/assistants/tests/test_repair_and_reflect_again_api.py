from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from intel_core.models import Document
from unittest.mock import patch


class RepairAndReflectAgainAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Fixer", specialty="x")
        self.document = Document.objects.create(title="Doc", content="t", source_type="url")
        self.assistant.documents.add(self.document)

    @patch("assistants.views.repair.repair_progress")
    def test_repair_documents(self, mock_repair):
        mock_repair.return_value = "ok"
        url = f"/api/v1/assistants/{self.assistant.slug}/repair_documents/"
        resp = self.client.post(url, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_repair.assert_called_once()
        self.assertIn("documents", resp.json())

    @patch("assistants.views.repair.AssistantReflectionEngine.reflect_on_document")
    def test_reflect_again_all(self, mock_reflect):
        mock_reflect.return_value = ("sum", [], None)
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect_again/"
        resp = self.client.post(url, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_reflect.assert_called_once_with(self.document)

    @patch("assistants.views.repair.AssistantReflectionEngine.reflect_on_document")
    def test_reflect_again_single(self, mock_reflect):
        mock_reflect.return_value = ("sum", [], None)
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect_again/?doc_id={self.document.id}"
        resp = self.client.post(url, format="json")
        self.assertEqual(resp.status_code, 200)
        mock_reflect.assert_called_once_with(self.document)
