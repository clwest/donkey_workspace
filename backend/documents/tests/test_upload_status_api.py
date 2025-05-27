import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import JobStatus
import uuid

class UploadStatusAPITest(APITestCase):
    def setUp(self):
        self.job = JobStatus.objects.create(
            status="processing",
            progress=50,
            stage="embedding",
            current_chunk=2,
            total_chunks=4,
            message="processing",
            session_id=uuid.uuid4(),
        )

    def test_upload_status_endpoint(self):
        url = f"/api/documents/upload-status/{self.job.session_id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["stage"], "embedding")
        self.assertEqual(data["percent_complete"], 50)
        self.assertEqual(data["current_chunk"], 2)
        self.assertEqual(data["total_chunks"], 4)
        self.assertEqual(data["message"], "processing")
