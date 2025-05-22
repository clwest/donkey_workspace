
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantMemoryChain
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from memory.models import MemoryEntry
from project.models import Project

class MemoryDocumentsAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="aud", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="DocBot", specialty="docs")
        self.empty = Assistant.objects.create(name="Empty", specialty="none")

        # Doc1 full embedding
        self.doc1 = Document.objects.create(title="Doc1", content="t", source_type="url")
        for i in range(3):
            chunk = DocumentChunk.objects.create(
                document=self.doc1,
                order=i,
                text="a",
                tokens=5,
                fingerprint=f"d1{i}"
            )
            embed = EmbeddingMetadata.objects.create(model_used="t", num_tokens=5, vector=[0.0, 0.0])
            chunk.embedding = embed
            chunk.save()
        MemoryEntry.objects.create(event="e1", summary="s1", assistant=self.assistant, document=self.doc1)
        self.assistant.documents.add(self.doc1)

        # Doc2 zero embedding
        self.doc2 = Document.objects.create(title="Doc2", content="t", source_type="url")
        for i in range(2):
            DocumentChunk.objects.create(
                document=self.doc2,
                order=i,
                text="b",
                tokens=5,
                fingerprint=f"d2{i}"
            )
        MemoryEntry.objects.create(event="e2", summary="s2", assistant=self.assistant, document=self.doc2)

        # Doc3 partial via memory chain
        self.doc3 = Document.objects.create(title="Doc3", content="t", source_type="url")
        for i in range(2):
            chunk = DocumentChunk.objects.create(
                document=self.doc3,
                order=i,
                text="c",
                tokens=5,
                fingerprint=f"d3{i}"
            )
            if i == 0:
                em = EmbeddingMetadata.objects.create(model_used="t", num_tokens=5, vector=[0.1, 0.1])
                chunk.embedding = em
                chunk.save()
        mem3 = MemoryEntry.objects.create(event="e3", summary="s3", assistant=self.assistant, document=self.doc3)
        project = Project.objects.create(user=self.user, title="P", slug="p", assistant=self.assistant)
        chain = AssistantMemoryChain.objects.create(project=project, title="C")
        chain.memories.add(mem3)

    def test_no_documents(self):
        url = f"/api/assistants/{self.empty.slug}/memory-documents/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_document_stats(self):
        url = f"/api/assistants/{self.assistant.slug}/memory-documents/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = {d["slug"]: d for d in resp.json()}
        self.assertEqual(len(data), 3)
        self.assertEqual(data[self.doc1.slug]["embedding_coverage"], 100.0)
        self.assertEqual(data[self.doc2.slug]["embedding_coverage"], 0.0)
        self.assertEqual(data[self.doc3.slug]["embedding_coverage"], 50.0)
        self.assertEqual(data[self.doc1.slug]["last_chunk_summary"], "s1")
