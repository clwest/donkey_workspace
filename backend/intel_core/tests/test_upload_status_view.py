import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import Document, DocumentProgress


class UploadStatusViewTest(APITestCase):
    def setUp(self):
        self.doc = Document.objects.create(
            title="Doc",
            content="hello world",
            source_type="pdf",
            token_count_int=123,
        )
        self.progress = DocumentProgress.objects.create(
            document=self.doc,
            title="Doc",
            total_chunks=4,
            processed=2,
            embedded_chunks=1,
            status="in_progress",
        )
        self.doc.metadata = {"progress_id": str(self.progress.progress_id)}
        self.doc.save(update_fields=["metadata"])

    def test_upload_status(self):
        url = f"/api/v1/intel/upload/status/{self.doc.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["chunk_count"], 4)
        self.assertEqual(data["embedded_count"], 1)
        self.assertEqual(data["status"], "queued")
