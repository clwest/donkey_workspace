import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from memory.models import SymbolicMemoryAnchor, MemoryEntry


class OnboardingGlossaryAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_glossary_boot(self):
        SymbolicMemoryAnchor.objects.create(slug="a", label="A", description="d")
        SymbolicMemoryAnchor.objects.create(slug="b", label="B", description="d")
        SymbolicMemoryAnchor.objects.create(slug="c", label="C", description="d")
        resp = self.client.get("/api/onboarding/glossary_boot/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["results"]), 3)

    def test_teach_anchor(self):
        anchor = SymbolicMemoryAnchor.objects.create(slug="teach", label="Teach", description="desc")
        resp = self.client.post("/api/onboarding/teach_anchor/", {"anchor_slug": "teach"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(MemoryEntry.objects.count(), 1)
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "acquired")
