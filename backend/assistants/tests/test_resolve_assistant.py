import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import pytest
from assistants.models import Assistant
from assistants.utils.resolve import resolve_assistant
from utils.resolvers import resolve_or_error

pytest.importorskip("django")


@pytest.mark.django_db
def test_resolve_assistant_slug_and_id():
    a = Assistant.objects.create(name="A", slug="a")
    by_slug = resolve_assistant("a")
    by_id = resolve_assistant(str(a.id))
    assert by_slug == a
    assert by_id == a


@pytest.mark.django_db
def test_resolve_or_error_generic():
    a = Assistant.objects.create(name="B", slug="b")
    obj = resolve_or_error(a.slug, Assistant)
    assert obj == a
    obj2 = resolve_or_error(str(a.id), Assistant)
    assert obj2 == a
    with pytest.raises(Exception):
        resolve_or_error("missing", Assistant)
