import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import pytest
from io import StringIO
from django.core.management import call_command
from assistants.models import Assistant
from assistants.models.demo import DemoUsageLog

pytest.importorskip("django")


@pytest.mark.django_db
def test_feedback_gaps_cli(capsys):
    a = Assistant.objects.create(
        name="Demo", slug="demo", demo_slug="demo", is_demo=True
    )
    for i in range(6):
        DemoUsageLog.objects.create(
            session_id=f"s{i}", demo_slug="demo", converted_at="2024-01-01"
        )
    out = StringIO()
    call_command("demo_feedback_gaps", stdout=out)
    assert "demo" in out.getvalue()
