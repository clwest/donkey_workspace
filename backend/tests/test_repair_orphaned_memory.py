import pytest
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import MemoryEntry

pytest.importorskip("django")


@pytest.mark.django_db
def test_repair_orphaned_memory_command():
    assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
    mem = MemoryEntry(event="hello", assistant=assistant)
    # bypass save() auto context creation
    MemoryEntry.objects.bulk_create([mem])
    assert mem.context_id is None

    call_command("repair_orphaned_memory")

    mem.refresh_from_db()
    assert mem.context_id == assistant.memory_context_id
