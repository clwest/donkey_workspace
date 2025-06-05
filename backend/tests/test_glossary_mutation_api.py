import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog


class GlossaryMutationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A")
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="align",
            label="alignment",
            suggested_label="goal coordination",
            mutation_source="rag_auto_suggest",
        )
        RAGGroundingLog.objects.create(
            assistant=self.assistant,
            fallback_triggered=True,
            expected_anchor="align",
            glossary_boost_type="chunk",
        )

    def test_list_and_accept_mutation(self):
        resp = self.client.get("/api/glossary/mutations/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)
        mid = resp.data["results"][0]["id"]
        self.assertEqual(resp.data["results"][0]["suggested_label"], "goal coordination")

        resp2 = self.client.post(f"/api/glossary/mutations/{mid}/accept")
        self.assertEqual(resp2.status_code, 200)
        self.anchor.refresh_from_db()
        self.assertEqual(self.anchor.label, "goal coordination")
        self.assertEqual(self.anchor.mutation_status, "applied")
