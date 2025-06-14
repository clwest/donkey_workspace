import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from io import StringIO
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
import pytest

pytest.importorskip("django")


@pytest.mark.django_db
def test_validate_anchors_cli_reports_orphans():
    assistant = Assistant.objects.create(name="A", slug="a")
    SymbolicMemoryAnchor.objects.create(
        slug="term-x", label="Term X", memory_context=assistant.memory_context
    )
    out = StringIO()
    call_command("validate_anchors", stdout=out)
    assert "term-x" in out.getvalue()
