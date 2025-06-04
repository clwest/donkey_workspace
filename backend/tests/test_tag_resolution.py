import pytest

pytest.importorskip("django")

from tags.models import Tag
from assistants.utils.reflection_helpers import resolve_tags_from_names


def test_resolve_tags_uses_existing_slug(db):
    Tag.objects.create(name="User Engagement")
    tags = resolve_tags_from_names(["user engagement"])
    assert len(tags) == 1
    assert Tag.objects.count() == 1
    assert tags[0].slug == "user-engagement"
