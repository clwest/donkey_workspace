import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from memory.models import MemoryEntry
from mcp_core.models import Tag
from memory.serializers import MemoryEntrySerializer

class MemoryPreviewTest(TestCase):
    def test_preview_fallback_and_trigger(self):
        t1 = Tag.objects.create(name="glossary-miss")
        t2 = Tag.objects.create(name="zk-rollup")
        mem = MemoryEntry.objects.create(event="", triggered_by="Glossary Anchor Miss: zk-rollup")
        mem.tags.set([t1, t2])

        self.assertEqual(mem.content_preview, "\U0001F9E0 Tags: #glossary-miss, #zk-rollup")

        data = MemoryEntrySerializer(mem).data
        self.assertEqual(data["triggered_by"], "Glossary Anchor Miss: zk-rollup")
