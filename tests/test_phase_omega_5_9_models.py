import pytest

pytest.importorskip("django")

from assistants.models import Assistant, IdentityAnchor, MythpathEvent, TemporalMythpathRecord
from agents.models import CodexInheritanceLink, CodexLineageThread


def test_phase_omega_5_9_models_create(db):
    mentor = Assistant.objects.create(name="A", specialty="seer")
    child = Assistant.objects.create(name="B", specialty="sage")
    anchor = IdentityAnchor.objects.create(assistant=mentor, codex_vector={"a": 1}, memory_origin="seed")
    link = CodexInheritanceLink.objects.create(mentor=mentor, child=child)
    thread = CodexLineageThread.objects.create(assistant=child, lineage_notes="start")
    record = TemporalMythpathRecord.objects.create(assistant=child)
    event = MythpathEvent.objects.create(assistant=child, event_type="test", description="d")

    assert anchor.assistant == mentor
    assert link.child == child
    assert thread.assistant == child
    assert record.assistant == child
    assert event.event_type == "test"
