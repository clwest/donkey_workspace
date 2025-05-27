from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantThoughtLog
from agents.models.lore import SwarmMemoryEntry
from intel_core.models import Document, DocumentSet


class AssistantFromDocumentSetAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.doc1 = Document.objects.create(
            title="Doc1", content="t1", source_type="url"
        )
        self.doc2 = Document.objects.create(
            title="Doc2", content="t2", source_type="url"
        )
        self.doc_set = DocumentSet.objects.create(title="Set1")
        self.doc_set.documents.set([self.doc1, self.doc2])
        self.url = "/assistants/from-document-set/"

    @patch("assistants.views.assistants.get_embedding_for_text")
    def test_create_assistant(self, mock_embed):
        mock_embed.return_value = [0.0] * 1536
        resp = self.client.post(
            self.url,
            {
                "document_set_id": str(self.doc_set.id),
                "name": "Helper",
                "personality": "supportive",
                "tone": "empathetic",
                "preferred_model": "gpt-4o",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        assistant_id = resp.json()["assistant_id"]
        assistant = Assistant.objects.get(id=assistant_id)
        self.assertEqual(assistant.document_set, self.doc_set)
        self.assertEqual(
            AssistantThoughtLog.objects.filter(assistant=assistant).count(), 1
        )
        self.assertTrue(
            SwarmMemoryEntry.objects.filter(title__icontains="Summon").exists()
        )
        prompt_text = assistant.system_prompt.content
        self.assertIn("quote from any transcript-based memory", prompt_text)
        self.assertIn("Avoid hallucinated refusals", prompt_text)
