import pytest

pytest.importorskip("django")

from assistants.models import Assistant, AssistantRelayMessage, AssistantThoughtLog


def test_phase_omega_5_5_1_relay_tracking(db):
    a1 = Assistant.objects.create(name="A", specialty="seer")
    a2 = Assistant.objects.create(name="B", specialty="sage")
    msg = AssistantRelayMessage.objects.create(sender=a1, recipient=a2, content="hi")
    assert not msg.delivered
    msg.mark_delivered()
    assert msg.delivered
    log = AssistantThoughtLog.objects.create(assistant=a2, thought="r", thought_type="reflection")
    msg.mark_responded(thought_log=log)
    msg.refresh_from_db()
    assert msg.responded
    assert msg.thought_log == log
