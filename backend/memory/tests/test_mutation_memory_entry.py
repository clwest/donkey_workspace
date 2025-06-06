import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, MemoryEntry


class MutationMemoryEntryTests(TestCase):
    def test_accept_mutation_creates_memory_entry(self):
        assistant = Assistant.objects.create(name="A", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(
            slug="zk",
            label="zk",
            suggested_label="zk rollup",
            assistant=assistant,
        )
        client = APIClient()
        resp = client.post(f"/api/glossary/mutations/{anchor.id}/accept")
        self.assertEqual(resp.status_code, 200)
        mems = MemoryEntry.objects.filter(anchor=anchor, type="mutation")
        self.assertEqual(mems.count(), 1)
        mem = mems.first()
        self.assertIn("zk", mem.summary)
        self.assertIn("zk rollup", mem.summary)
        self.assertTrue(mem.tags.filter(slug="glossary-mutation").exists())
        self.assertFalse(mem.symbolic_change)
        anchor.refresh_from_db()
        self.assertIn(str(mem.id), anchor.explanation)
