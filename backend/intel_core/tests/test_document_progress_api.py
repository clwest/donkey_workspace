import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import Document, DocumentProgress


class DocumentProgressAPITest(APITestCase):
    def setUp(self):
        self.document = Document.objects.create(
            title="Chunk 1",
            content="c",
            source_type="pdf",
        )
        self.progress = DocumentProgress.objects.create(
            document=self.document,
            title="Test PDF",
            total_chunks=5,
            processed=2,
            embedded_chunks=0,
            failed_chunks=[1],
            status="in_progress",
        )
        self.document.metadata = {"progress_id": str(self.progress.progress_id)}
        self.document.save(update_fields=["metadata"])

    def test_progress_endpoint(self):
        url = f"/api/v1/intel/documents/{self.progress.progress_id}/progress/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_chunks"], 5)
        self.assertEqual(data["processed"], 2)
        self.assertEqual(data["failed_chunks"], [1])

    def test_ingest_exception_marks_progress_failed(self):
        import sys
        import types
        from types import SimpleNamespace
        from unittest.mock import patch

        sys.modules.setdefault("openai", types.ModuleType("openai")).OpenAI = (
            lambda: None
        )
        spacy_stub = types.ModuleType("spacy")
        spacy_stub.load = lambda name: None
        sys.modules.setdefault("spacy", spacy_stub)
        numpy_stub = types.ModuleType("numpy")

        class FakeNdArray(list):
            pass

        numpy_stub.ndarray = FakeNdArray
        sys.modules.setdefault("numpy", numpy_stub)

        from backend.core.services import document_service as doc_service

        DocumentProgress.objects.all().delete()

        dummy_chunk = SimpleNamespace(page_content="some content " * 20, metadata={})

        with patch.object(doc_service, "PDFPlumberLoader") as loader_cls, patch.object(
            doc_service, "process_pdfs", side_effect=Exception("boom")
        ):
            loader_instance = loader_cls.return_value
            loader_instance.load_and_split.return_value = [dummy_chunk]

            doc_service.ingest_pdfs(["dummy.pdf"])

        progress = DocumentProgress.objects.first()
        self.assertEqual(progress.status, "failed")
        self.assertEqual(progress.error_message, "boom")
