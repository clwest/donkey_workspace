import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from django.utils.text import slugify

from intel_core.models import DocumentChunk, Document
from memory.models import SymbolicMemoryAnchor, GlossaryChangeEvent
from assistants.models import Assistant

class BoostGlossaryTermTests(TestCase):
    def test_boost_term_creates_anchor_and_event(self):
        doc = Document.objects.create(title="t")
        chunk = DocumentChunk.objects.create(
            document=doc,
            order=1,
            text="zk rollup is cool",
            tokens=5,
            fingerprint="f1",
        )
        client = APIClient()
        resp = client.post("/api/intel/glossary/boost/term/", {"term": "zk rollup", "boost": 0.2})
        self.assertEqual(resp.status_code, 200)
        anchor = SymbolicMemoryAnchor.objects.get(slug=slugify("zk rollup"))
        chunk.refresh_from_db()
        self.assertEqual(chunk.anchor, anchor)
        self.assertAlmostEqual(chunk.glossary_boost, 0.2)
        self.assertEqual(GlossaryChangeEvent.objects.filter(term="zk rollup").count(), 1)

