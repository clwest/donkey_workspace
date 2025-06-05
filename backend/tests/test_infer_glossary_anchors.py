import pytest

pytest.importorskip("django")

from django.core.management import call_command
from assistants.models import Assistant
from memory.models import MemoryEntry, SymbolicMemoryAnchor


@pytest.mark.django_db
def test_infer_glossary_anchors_from_memory():
    a = Assistant.objects.create(name="ClarityBot", slug="clarity")
    MemoryEntry.objects.create(
        assistant=a,
        event="Goal threading across objectives ensures continuity",
        summary="Goal threading keeps plans aligned",
    )

    call_command("infer_glossary_anchors", "--assistant", a.slug, "--source", "memory")

    anchor = SymbolicMemoryAnchor.objects.get(slug="threading")
    assert anchor.mutation_status == "pending"
    assert anchor.mutation_source == "assistant_memory_inferred"
    assert anchor.assistant == a
