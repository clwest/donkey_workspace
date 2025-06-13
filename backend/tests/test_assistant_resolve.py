import pytest
from assistants.models import Assistant
from assistants.utils.resolve import resolve_assistant

pytest.importorskip("django")


@pytest.mark.django_db
def test_resolve_by_slug():
    a = Assistant.objects.create(name="A", slug="slug-a")
    assert resolve_assistant("slug-a") == a


@pytest.mark.django_db
def test_resolve_by_id():
    a = Assistant.objects.create(name="A", slug="slug-b")
    assert resolve_assistant(str(a.id)) == a


@pytest.mark.django_db
def test_resolve_invalid_uuid_slug():
    a = Assistant.objects.create(name="A", slug="donk")
    # value looks like uuid prefix but is not a valid uuid
    assert resolve_assistant("donk") == a


@pytest.mark.django_db
def test_resolve_invalid_value_returns_none():
    Assistant.objects.create(name="A", slug="slug-c")
    assert resolve_assistant("nope") is None
