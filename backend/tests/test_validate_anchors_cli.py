# flake8: noqa
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from io import StringIO
from django.core.management import call_command
from unittest.mock import patch

from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from mcp_core.models import Tag
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


@pytest.mark.django_db
@patch("embeddings.helpers.helper_tagging.generate_tags_for_memory")
def test_validate_anchors_cli_slugifies_tags(mock_gen_tags):
    assistant = Assistant.objects.create(name="A", slug="a")
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="tm", label="Task management", memory_context=assistant.memory_context
    )
    Tag.objects.create(slug="task-management", name="task management")
    mock_gen_tags.return_value = ["task management"]
    out = StringIO()
    call_command("validate_anchors", stdout=out)
    anchor.refresh_from_db()
    assert anchor.tags.filter(slug="task-management").exists()
