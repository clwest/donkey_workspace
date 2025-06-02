import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from intel_core.tasks import process_url_upload


class UUIDSafetyTests(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="s", slug="a")

    def test_ingest_view_invalid_session_uuid(self):
        resp = self.client.post(
            "/api/intel/ingest/",
            {
                "source_type": "text",
                "assistant_id": self.assistant.slug,
                "text": "hi",
                "session_id": "debug-session",
            },
        )
        self.assertEqual(resp.status_code, 200)

    def test_task_invalid_job_id_returns_zero(self):
        result = process_url_upload(urls=["http://ex.com"], job_id="debug-job")
        self.assertEqual(result, 0)
