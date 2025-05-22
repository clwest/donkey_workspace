import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from unittest.mock import patch
from intel_core.models import JobStatus


class DocumentImportAPITest(APITestCase):
    url = "/api/v1/documents/import/"

    @patch("documents.views.import_view.process_pdf_upload.delay")
    def test_import_returns_job_id(self, mock_task):
        with open(__file__, "rb") as f:
            resp = self.client.post(self.url, {"file": f})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("job_id", data)
        mock_task.assert_called()
        self.assertTrue(JobStatus.objects.filter(job_id=data["job_id"]).exists())
