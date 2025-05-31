from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from intel_core.models import Document
from memory.models import MemoryEntry
from unittest.mock import patch

class AssistantIngestReviewAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Rev", specialty="s")
        self.document = Document.objects.create(title="Doc", content="x", source_type="url")

    @patch("assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document")
    def test_review_ingest_creates_memory(self, mock_reflect):
        mock_reflect.return_value = ("sum", ["insight 1"])
        url = f"/api/v1/assistants/{self.assistant.slug}/review-ingest/{self.document.id}/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(MemoryEntry.objects.filter(assistant=self.assistant).exists())

