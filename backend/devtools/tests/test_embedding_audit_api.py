import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from memory.models import MemoryEntry
from assistants.models import Assistant
from embeddings.models import Embedding, EmbeddingDebugTag


class EmbeddingAuditAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="audit", password="pw", is_staff=True)
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Auditor", specialty="gen")
        mem = MemoryEntry.objects.create(event="hey", assistant=self.assistant)
        ct = ContentType.objects.get_for_model(MemoryEntry)
        Embedding.objects.create(
            content_type=ct,
            object_id=str(mem.id),
            content_id=f"memoryentry:{mem.id}",
            embedding=[0.0] * 5,
        )
        emb = mem.embeddings.first()
        EmbeddingDebugTag.objects.create(embedding=emb, reason="orphaned-object")

    def test_audit_endpoint(self):
        resp = self.client.get("/api/dev/embedding-audit/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertIn("recent_orphans", data)
        self.assertIn("context_audit", data)
        entry = data["context_audit"][0]
        self.assertEqual(entry["assistant"], self.assistant.slug)
        self.assertEqual(entry["assistant_name"], self.assistant.name)
        self.assertEqual(entry["context_id"], str(self.assistant.memory_context_id))
        self.assertEqual(entry["count"], 1)


