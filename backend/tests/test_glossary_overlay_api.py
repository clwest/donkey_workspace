import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from memory.models import SymbolicMemoryAnchor


class GlossaryOverlayAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        SymbolicMemoryAnchor.objects.create(
            slug="mypath",
            label="MythPath",
            glossary_guidance="help text",
            display_tooltip=True,
            display_location=["dashboard", "assistant_detail"],
        )
        SymbolicMemoryAnchor.objects.create(
            slug="hidden",
            label="Hidden",
            glossary_guidance="hide",
            display_tooltip=False,
            display_location=["dashboard"],
        )

    def test_overlay_location_filter(self):
        resp = self.client.get("/api/terms/glossary_overlay/?location=dashboard")
        self.assertEqual(resp.status_code, 200)
        results = resp.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["slug"], "mypath")
        self.assertEqual(results[0]["location"], "dashboard")
