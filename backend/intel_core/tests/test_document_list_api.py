import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import Document
from assistants.models import Assistant


class DocumentListAPITest(APITestCase):
    def setUp(self):
        self.doc1 = Document.objects.create(title="Doc", content="a", source_type="url")
        self.doc2 = Document.objects.create(title="Doc", content="b", source_type="url")
        self.doc3 = Document.objects.create(title="Doc", content="c", source_type="pdf")
        self.other = Document.objects.create(
            title="Other", content="x", source_type="url"
        )
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.assistant.documents.add(self.other)

    def test_unique_documents_returned(self):
        resp = self.client.get("/api/intel/documents/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        titles = {(d["title"], d["source_type"]) for d in data}
        self.assertEqual(len(data), len(titles))

    def test_exclude_for_param(self):
        resp = self.client.get(
            f"/api/intel/documents/?exclude_for={self.assistant.slug}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [d["id"] for d in resp.json()]
        self.assertNotIn(str(self.other.id), ids)

    def test_unlinked_duplicate_returned(self):
        """Unlinked duplicate documents should still appear."""
        self.assistant.documents.add(self.doc1)
        resp = self.client.get(
            f"/api/intel/documents/?exclude_for={self.assistant.slug}"
        )
        self.assertEqual(resp.status_code, 200)
        ids = [d["id"] for d in resp.json()]
        self.assertIn(str(self.doc2.id), ids)
        self.assertIn(str(self.doc3.id), ids)
        self.assertNotIn(str(self.doc1.id), ids)
