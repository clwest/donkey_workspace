from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata


class RagSelfTestAPITest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.assistant = Assistant.objects.create(name="Rag", specialty="r")
        anchor = SymbolicMemoryAnchor.objects.create(slug="rag", label="RAG")
        doc = Document.objects.create(title="D", content="c", source_url="http://x.com")
        chunk = DocumentChunk.objects.create(
            document=doc,
            order=0,
            text="RAG term explained",
            tokens=5,
            fingerprint="r1",
            anchor=anchor,
            is_glossary=True,
            glossary_score=0.9,
        )
        emb = EmbeddingMetadata.objects.create(
            model_used="t", num_tokens=5, vector=[0.1]
        )
        chunk.embedding = emb
        chunk.save()
        self.assistant.documents.add(doc)

    def test_rag_self_test_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/rag_self_test/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertEqual(data["tested"], 1)
        self.assertEqual(data["issues_found"], 0)
