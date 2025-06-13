import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from mcp_core.models import DevDoc
from intel_core.models import Document
from assistants.models.reflection import AssistantReflectionLog


def test_relink_devdocs_command_links_and_reflects():
    devdoc = DevDoc.objects.create(
        title="Sample Doc", slug="sample-doc", content="test"
    )
    doc = Document.objects.create(title="Sample Doc", slug="sample-doc", content="test")
    devdoc.linked_document = None
    devdoc.save(update_fields=["linked_document"])

    call_command("relink_devdocs", "--reflect")
    devdoc.refresh_from_db()
    assert devdoc.linked_document_id == doc.id
    assert AssistantReflectionLog.objects.filter(document=doc).exists()


def test_seed_dev_docs_idempotent():
    call_command("seed_dev_docs")
    count = DevDoc.objects.count()
    call_command("seed_dev_docs")
    assert DevDoc.objects.count() == count
