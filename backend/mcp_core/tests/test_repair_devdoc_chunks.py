import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from mcp_core.models import DevDoc
from intel_core.models import Document, DocumentChunk


def test_repair_devdoc_chunks_creates_chunks():
    devdoc = DevDoc.objects.create(title="T", slug="t", content="hello world")
    doc = Document.objects.create(title="T", slug="t", content="hello world")
    devdoc.linked_document = doc
    devdoc.save(update_fields=["linked_document"])
    assert DocumentChunk.objects.count() == 0
    call_command("repair_devdoc_chunks")
    assert DocumentChunk.objects.filter(document=doc).exists()
