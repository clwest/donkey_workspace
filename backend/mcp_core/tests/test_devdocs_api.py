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

class DevDocListAPITest(APITestCase):
    def setUp(self):
        DevDoc.objects.create(title="Doc 1", content="c1")

    def test_devdoc_list(self):
        resp = self.client.get("/api/v1/mcp/dev_docs/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["results"][0]["title"] == "Doc 1"
