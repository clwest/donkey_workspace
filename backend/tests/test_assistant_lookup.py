import pytest
from assistants.models import Assistant
from assistants.utils.assistant_lookup import resolve_assistant

pytest.importorskip("django")


@pytest.mark.django_db
def test_resolve_assistant_by_slug():
    a = Assistant.objects.create(name="A", slug="a")
    assert resolve_assistant("a") == a


@pytest.mark.django_db
def test_resolve_assistant_by_id():
    a = Assistant.objects.create(name="A", slug="a")
    assert resolve_assistant(str(a.id)) == a


@pytest.mark.django_db
def test_resolve_assistant_by_context():
    a = Assistant.objects.create(name="A", slug="a", memory_context_id="ctx")
    assert resolve_assistant("ctx") == a
