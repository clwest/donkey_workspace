import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from mcp_core.models import DevDoc


class DevDocSummaryAPITest(APITestCase):
    def test_summarize_no_docs(self):
        DevDoc.objects.all().delete()
        resp = self.client.post("/api/v1/mcp/dev_docs/summarize/")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json().get("error"), "No DevDocs found.")
