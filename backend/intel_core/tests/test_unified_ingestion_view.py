import os
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
pytest.importorskip("django")
import django

django.setup()

from rest_framework.test import APITestCase
from unittest.mock import patch
import uuid


class UnifiedIngestionViewTests(APITestCase):
    @patch("intel_core.views.ingestion.DocumentService.ingest")
    def test_skip_reason_propagated(self, mock_ingest):
        mock_ingest.return_value = [
            {
                "status": "skipped",
                "reason": "Transcript could not be retrieved",
                "url": "https://youtu.be/123",
            }
        ]
        resp = self.client.post(
            "/api/intel/ingest/",
            {
                "source_type": "youtube",
                "videos": "https://youtu.be/123",
                "assistant_id": str(uuid.uuid4()),
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("reason"), "Transcript could not be retrieved")

