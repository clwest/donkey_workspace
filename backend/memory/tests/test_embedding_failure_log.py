import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from intel_core.models import DocumentSet
from memory.models import MemoryEmbeddingFailureLog


class MemoryDiffViewTest(APITestCase):
    def setUp(self):
        self.doc_set = DocumentSet.objects.create(title="T")
        MemoryEmbeddingFailureLog.objects.create(
            document_set=self.doc_set,
            chunk_index=1,
            text="bad chunk",
            error_message="fail",
        )

    def test_diff_endpoint(self):
        url = f"/api/v1/memory/diff/{self.doc_set.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["document_set_id"], str(self.doc_set.id))
        self.assertEqual(len(data["chunks"]), 1)
