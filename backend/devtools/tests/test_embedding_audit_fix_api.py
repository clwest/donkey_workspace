import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from embeddings.models import Embedding, EmbeddingDebugTag
from intel_core.models import DocumentChunk


class EmbeddingAuditFixAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="fixer", password="pw", is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        chunk = DocumentChunk.objects.create(
            document_id="d", order=1, text="t", tokens=1
        )
        ct = ContentType.objects.get_for_model(DocumentChunk)
        self.emb = Embedding.objects.create(
            content_type=ct,
            object_id="bad",  # wrong id
            content_id="documentchunk:bad",
            embedding=[0.0] * 5,
        )
        self.tag = EmbeddingDebugTag.objects.create(
            embedding=self.emb,
            reason="wrong FK",
        )

    def test_fix_endpoint_repairs_embedding(self):
        url = f"/api/dev/embedding-audit/{self.tag.id}/fix/"
        resp = self.client.patch(url, format="json")
        self.assertEqual(resp.status_code, 200)
        self.emb.refresh_from_db()
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.repair_status, "repaired")
        self.assertEqual(self.tag.repair_attempts, 1)
        self.assertEqual(self.emb.object_id, str(self.emb.content_object.id))

    def test_ignore_action(self):
        url = f"/api/dev/embedding-audit/{self.tag.id}/fix/"
        resp = self.client.patch(url, {"action": "ignore"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.repair_status, "ignored")
