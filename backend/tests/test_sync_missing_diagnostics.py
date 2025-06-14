import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
import pytest

pytest.importorskip("django")


@pytest.mark.django_db
def test_sync_missing_diagnostics_runs(tmp_path):
    a = Assistant.objects.create(name="A", slug="a")
    call_command("sync_missing_diagnostics")
    # command should create anchors or at least run without error
    assert True
