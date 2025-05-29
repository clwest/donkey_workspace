import pytest

pytest.importorskip("django")

from assistants.models import Assistant, AssistantRelayMessage


def test_phase_omega_5_4_3_models_create(db):
    a1 = Assistant.objects.create(name="A", specialty="seer")
    a2 = Assistant.objects.create(name="B", specialty="sage")
    msg = AssistantRelayMessage.objects.create(sender=a1, recipient=a2, content="hi")
    assert msg.status == "pending"
    msg.mark_delivered()
    msg.refresh_from_db()
    assert msg.status == "delivered"
    assert msg.delivered_at is not None
