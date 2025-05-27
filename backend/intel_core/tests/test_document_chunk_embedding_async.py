import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()

from django.test import TestCase
from unittest.mock import patch
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from intel_core.utils import processing
from embeddings.models import Embedding
from django.contrib.contenttypes.models import ContentType


class DocumentChunkEmbeddingTests(TestCase):
    def test_tasks_scheduled_for_chunks(self):
        doc = Document.objects.create(title="T", content="a" * 120)
        with patch("intel_core.utils.processing.embed_and_store.delay") as mock_delay:
            with patch("intel_core.utils.processing.generate_chunks", return_value=["a" * 50, "b" * 50]):
                with patch("intel_core.utils.processing.generate_chunk_fingerprint", side_effect=["fp1", "fp2"]):
                    processing._create_document_chunks(doc)
        self.assertEqual(mock_delay.call_count, 2)
        self.assertEqual(DocumentChunk.objects.filter(document=doc).count(), 2)

    def test_embedding_signal_links_metadata(self):
        doc = Document.objects.create(title="X", content="y")
        chunk = DocumentChunk.objects.create(
            document=doc,
            order=0,
            text="c",
            tokens=1,
            chunk_type="body",
            fingerprint="fp",
        )
        ct = ContentType.objects.get_for_model(DocumentChunk)
        Embedding.objects.create(
            content_type=ct,
            object_id=chunk.id,
            content_id=str(chunk.id),
            content=chunk.text,
            embedding=[0.0] * 1536,
        )
        chunk.refresh_from_db()
        self.assertIsNotNone(chunk.embedding)
        self.assertTrue(EmbeddingMetadata.objects.filter(embedding_id=chunk.embedding.embedding_id).exists())
