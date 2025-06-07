import pytest
from django.utils import timezone

pytest.importorskip("django")

from assistants.models import Assistant
from assistants.helpers.demo_utils import generate_assistant_from_demo
from assistants.models.trail import TrailMarkerLog
from memory.models import MemoryEntry


def test_trail_summary_ready(db):
    asst = Assistant.objects.create(name="T", slug="t")
    assert not asst.trail_summary_ready
    MemoryEntry.objects.create(
        assistant=asst,
        context=asst.memory_context,
        summary="born",
        type="milestone_summary",
    )
    assert asst.trail_summary_ready


def test_demo_conversion_marker(db):
    user = Assistant.objects.create(name="Demo", slug="d", is_demo=True, demo_slug="d")
    demo_clone = generate_assistant_from_demo("d", user)
    assert TrailMarkerLog.objects.filter(assistant=demo_clone, marker_type="demo_converted").exists()
