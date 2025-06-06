import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor


class GlossaryMutationEndpointTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.client = APIClient()
        self.pending = SymbolicMemoryAnchor.objects.create(
            slug="t1",
            label="Term1",
            mutation_source="reflection",
            assistant=self.assistant,
        )
        self.applied = SymbolicMemoryAnchor.objects.create(
            slug="t2",
            label="Term2",
            mutation_source="reflection",
            mutation_status="applied",
            assistant=self.assistant,
        )

    def test_default_pending_only(self):
        resp = self.client.get("/api/glossary/mutations/")
        self.assertEqual(resp.status_code, 200)
        ids = {r["id"] for r in resp.json()["results"]}
        self.assertIn(str(self.pending.id), ids)
        self.assertNotIn(str(self.applied.id), ids)

    def test_include_all(self):
        resp = self.client.get("/api/glossary/mutations/?include=all")
        self.assertEqual(resp.status_code, 200)
        ids = {r["id"] for r in resp.json()["results"]}
        self.assertIn(str(self.pending.id), ids)
        self.assertIn(str(self.applied.id), ids)
