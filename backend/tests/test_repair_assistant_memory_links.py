import pytest
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import MemoryEntry

pytest.importorskip("django")


@pytest.mark.django_db
def test_repair_assistant_memory_links():
    assistant = Assistant.objects.create(name="Fixer", specialty="gen")
    mem = MemoryEntry.objects.create(event="hi", context=assistant.memory_context)
    assert mem.assistant_id is None

    call_command("repair_assistant_memory_links", "--assistant", assistant.slug)

    mem.refresh_from_db()
    assert mem.assistant_id == assistant.id
