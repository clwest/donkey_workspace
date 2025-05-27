from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantThoughtLog
from agents.models.lore import SwarmMemoryEntry
from intel_core.models import Document


class AssistantFromDocumentsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.doc1 = Document.objects.create(
            title="Doc1", content="t1", source_type="url"
        )
        self.doc2 = Document.objects.create(
            title="Doc2", content="t2", source_type="url"
        )
        self.url = "/assistants/from-documents/"

    @patch("assistants.views.assistants.get_embedding_for_text")
    def test_create_assistant(self, mock_embed):
        mock_embed.return_value = [0.0] * 1536
        resp = self.client.post(
            self.url,
            {
                "document_ids": [str(self.doc1.id), str(self.doc2.id)],
                "name": "Helper",
                "personality": "supportive",
                "tone": "empathetic",
                "preferred_model": "gpt-4o",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        payload = resp.json()
        assistant_id = payload["assistant_id"]
        self.assertIn("slug", payload)
        assistant = Assistant.objects.get(id=assistant_id)
        self.assertEqual(payload["slug"], assistant.slug)
        self.assertEqual(assistant.documents.count(), 2)
        self.assertIsNotNone(assistant.document_set)
        self.assertEqual(
            AssistantThoughtLog.objects.filter(assistant=assistant).count(), 1
        )
        self.assertTrue(
            SwarmMemoryEntry.objects.filter(title__icontains="Summon").exists()
        )
        prompt_text = assistant.system_prompt.content
        self.assertIn("quote from any transcript-based memory", prompt_text)
        self.assertIn("Avoid hallucinated refusals", prompt_text)
