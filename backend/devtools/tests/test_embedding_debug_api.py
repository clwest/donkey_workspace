import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from memory.models import MemoryEntry
from embeddings.models import Embedding
from intel_core.models import EmbeddingMetadata
from assistants.models import Assistant


class EmbeddingDebugAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="embdebug", password="pw")
        self.client.force_authenticate(user=self.user)
        mem = MemoryEntry.objects.create(event="hello")
        ct = ContentType.objects.get_for_model(MemoryEntry)
        Embedding.objects.create(
            content_type=ct,
            object_id=str(mem.id),
            content_id=f"memoryentry:{mem.id}",
            embedding=[0.0] * 5,
        )
        EmbeddingMetadata.objects.create(model_used="test", num_tokens=1, vector=[0.0])

    def test_debug_endpoint(self):
        resp = self.client.get("/api/dev/embedding-debug/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("model_counts", data)
        self.assertIn("assistant_breakdown", data)
        self.assertIn("assistants_no_docs", data)
        self.assertIn("retrieval_checks", data)
        self.assertIn("repairable_contexts", data)

    def test_assistant_filter(self):
        assistant = Assistant.objects.create(name="A", slug="a")
        mem = MemoryEntry.objects.create(event="x", assistant=assistant)
        ct = ContentType.objects.get_for_model(MemoryEntry)
        Embedding.objects.create(
            content_type=ct,
            object_id=str(mem.id),
            content_id=f"memoryentry:{mem.id}",
            embedding=[0.1],
        )
        resp = self.client.get(f"/api/dev/embedding-debug/?assistant={assistant.slug}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(all(d["assistant__slug"] == assistant.slug for d in data["assistant_breakdown"]))
