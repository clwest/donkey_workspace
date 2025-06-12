import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from memory.models import MemoryEntry
from mcp_core.models import Tag
from assistants.models.reflection import AssistantReflectionLog
from assistants.serializers_pass import AssistantPreviewSerializer

@pytest.mark.django_db
def test_assistant_preview_fields():
    a = Assistant.objects.create(name="A", specialty="t", description="desc")
    tag = Tag.objects.create(slug="starter-chat", name="starter-chat")
    mem = MemoryEntry.objects.create(assistant=a, event="hi", full_transcript="hello")
    mem.tags.add(tag)
    AssistantReflectionLog.objects.create(assistant=a, title="r", summary="reflect")

    data = AssistantPreviewSerializer(a).data
    assert data["memory_count"] == 1
    assert data["starter_memory_excerpt"].startswith("hello")
    assert data["latest_reflection"] == "reflect"
