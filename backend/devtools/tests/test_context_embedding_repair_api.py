import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from assistants.models import Assistant
from memory.models import MemoryEntry
from embeddings.models import Embedding, EmbeddingDebugTag

class ContextEmbeddingRepairAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="ctxfix", password="pw", is_staff=True)
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Ctx", specialty="gen")
        self.mem = MemoryEntry.objects.create(event="hi", assistant=self.assistant)
        ct = ContentType.objects.get_for_model(MemoryEntry)
        self.emb = Embedding.objects.create(
            content_type=None,
            object_id=str(self.mem.id),
            content_id=f"memoryentry:{self.mem.id}",
            embedding=[0.0] * 5,
        )
        self.tag = EmbeddingDebugTag.objects.create(
            embedding=self.emb, reason="wrong FK"
        )
        self.context_id = self.mem.context_id

    def test_repair_context_embeddings(self):
        url = f"/api/dev/embedding-audit/{self.context_id}/repair/"
        resp = self.client.patch(url, format="json")
        self.assertEqual(resp.status_code, 200)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.repair_status, "repaired")

    def test_ignore_context_embeddings(self):
        url = f"/api/dev/embedding-audit/{self.context_id}/ignore/"
        resp = self.client.patch(url, format="json")
        self.assertEqual(resp.status_code, 200)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.repair_status, "ignored")
