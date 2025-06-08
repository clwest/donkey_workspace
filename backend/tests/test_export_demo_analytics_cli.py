import pytest
from io import StringIO
from django.utils import timezone
from django.core.management import call_command

from assistants.models import Assistant
from assistants.models.demo import DemoUsageLog
from assistants.models.demo_usage import DemoSessionLog

pytest.importorskip("django")


@pytest.mark.django_db
def test_export_no_filters():
    a = Assistant.objects.create(name="Demo", slug="demo", demo_slug="demo", is_demo=True)
    DemoSessionLog.objects.create(
        assistant=a,
        session_id="s1",
        message_count=3,
        starter_query="hello",
        converted_to_real_assistant=True,
        demo_interaction_score=7,
        likely_to_convert=True,
        tips_helpful=2,
    )
    DemoUsageLog.objects.create(
        session_id="s1",
        demo_slug="demo",
        user_rating=5,
        feedback_text="great",
        created_at=timezone.now(),
    )
    out = StringIO()
    call_command("export_demo_analytics", stdout=out)
    data = out.getvalue().strip().splitlines()
    assert len(data) == 2  # header + row
    assert data[0].startswith("session_id")


@pytest.mark.django_db
def test_export_date_and_slug_filters():
    a1 = Assistant.objects.create(name="A1", slug="a1", demo_slug="d1", is_demo=True)
    a2 = Assistant.objects.create(name="A2", slug="a2", demo_slug="d2", is_demo=True)
    now = timezone.now()
    DemoSessionLog.objects.create(assistant=a1, session_id="s1", starter_query="hi")
    DemoSessionLog.objects.create(assistant=a2, session_id="s2", starter_query="hi")
    DemoUsageLog.objects.create(session_id="s1", demo_slug="d1", created_at=now)
    DemoUsageLog.objects.create(session_id="s2", demo_slug="d2", created_at=now - timezone.timedelta(days=5))

    out = StringIO()
    start = (now - timezone.timedelta(days=1)).date().isoformat()
    call_command("export_demo_analytics", "--start=" + start, "--demo_slug=d1", stdout=out)
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert len(lines) == 2
    assert "s1" in lines[1]

