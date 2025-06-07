import pytest
from django.utils import timezone
from datetime import timedelta

pytest.importorskip("django")

from assistants.models import Assistant
from assistants.models.trail import TrailMarkerLog
from assistants.utils.trail_marker_summary import summarize_trail_markers


def test_trail_marker_summary(db):
    assistant = Assistant.objects.create(name="Zeno", slug="zeno")
    now = timezone.now()
    TrailMarkerLog.objects.create(
        assistant=assistant,
        marker_type="birth",
        timestamp=now - timedelta(days=3),
    )
    TrailMarkerLog.objects.create(
        assistant=assistant,
        marker_type="personalization",
        timestamp=now - timedelta(days=2),
    )
    TrailMarkerLog.objects.create(
        assistant=assistant,
        marker_type="first_chat",
        timestamp=now - timedelta(days=1),
    )
    mem = summarize_trail_markers(assistant)
    assert mem.is_summary
    assert mem.memory_type == "milestone"
    assert "was born" in mem.summary
    assert "began chatting" in mem.summary
