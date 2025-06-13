import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from intel_core.models import Document
from intel_core.services.document_service import DocumentService


class ReflectDocSlugId(APITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", slug="slug")
        self.document = Document.objects.create(title="T")

    def test_endpoint_slug_and_id(self):
        url = "/api/mcp/reflect_on_document/"
        data_slug = {
            "assistant_id": self.assistant.slug,
            "doc_id": str(self.document.id),
            "project_id": "p",
        }
        resp = self.client.post(url, data_slug, format="json")
        self.assertNotEqual(resp.status_code, 404)
        data_id = {
            "assistant_id": str(self.assistant.id),
            "doc_id": str(self.document.id),
            "project_id": "p",
        }
        resp2 = self.client.post(url, data_id, format="json")
        self.assertNotEqual(resp2.status_code, 404)
