import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
import uuid


class AcceptMutationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A")
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="term-x",
            label="Term X",
            mutation_status="pending",
        )

    def test_accept_mutation(self):
        resp = self.client.post(f"/api/glossary/mutations/{self.anchor.id}/accept/")
        self.assertEqual(resp.status_code, 200)
        self.anchor.refresh_from_db()
        self.assertEqual(self.anchor.mutation_status, "accepted")

    def test_invalid_id_404(self):
        bad_id = uuid.uuid4()
        resp = self.client.post(f"/api/glossary/mutations/{bad_id}/accept/")
        self.assertEqual(resp.status_code, 404)

