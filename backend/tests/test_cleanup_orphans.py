import pytest
from django.core.management import call_command
from io import StringIO

from assistants.models import Assistant

pytest.importorskip("django")


@pytest.mark.django_db
def test_cleanup_orphan_assistants_dry_run():
    Assistant.objects.create(name="Orphan", slug="orphan")
    out = StringIO()
    call_command("cleanup_orphan_assistants", "--dry-run", stdout=out)
    assert "orphan" in out.getvalue()
