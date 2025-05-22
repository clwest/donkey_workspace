import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import Document, DocumentProgress

class DocumentProgressAPITest(APITestCase):
    def setUp(self):
        self.progress = DocumentProgress.objects.create(
            title="Test PDF",
            total_chunks=5,
            processed=2,
            failed_chunks=[1],
            status="in_progress",
        )
        Document.objects.create(
            title="Chunk 1",
            content="c",
            source_type="pdf",
            metadata={"progress_id": str(self.progress.progress_id)},
        )

    def test_progress_endpoint(self):
        url = f"/api/v1/intel/documents/{self.progress.progress_id}/progress/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_chunks"], 5)
        self.assertEqual(data["processed"], 2)
        self.assertEqual(data["failed_chunks"], [1])
