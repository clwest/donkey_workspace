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
        self.doc_url = Document.objects.create(
            title="Doc", content="d", source_type="url", source_url="http://ex.com"
        )
        self.other = Document.objects.create(
            title="Other", content="x", source_type="url"
        )
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.assistant.documents.add(self.other)

    def test_limit_param(self):
        for i in range(60):
            Document.objects.create(title=f"X{i}", content="t", source_type="url")
        resp = self.client.get("/api/intel/documents/?limit=25")
        self.assertEqual(resp.status_code, 200)
        self.assertLessEqual(len(resp.json()), 25)

    def test_unique_documents_returned(self):
        resp = self.client.get("/api/intel/documents/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        combos = {(d["title"], d["source_type"], d.get("source_url")) for d in data}
        self.assertEqual(len(data), len(combos))

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
        self.assertIn(str(self.doc_url.id), ids)
        self.assertNotIn(str(self.doc1.id), ids)
