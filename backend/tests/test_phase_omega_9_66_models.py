import pytest

pytest.importorskip("django")

from assistants.models import Assistant


def test_avatar_and_tone_defaults(db):
    a = Assistant.objects.create(name="Test", specialty="t")
    assert a.avatar_style == "robot"
    assert a.tone_profile == "friendly"
