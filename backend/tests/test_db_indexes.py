import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.models.assistant import AssistantChatMessage
from memory.models import MemoryEntry

import pytest

pytest.importorskip("django")


def has_index(field):
    return getattr(MemoryEntry._meta.get_field(field), "db_index", False)


def test_index_flags():
    assert has_index("assistant")
    assert has_index("context")
    assert AssistantChatMessage._meta.get_field("session").db_index
