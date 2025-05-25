import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from memory.models import MemoryEntry
from mcp_core.models import Tag

from utils.role_collision import detect_role_collisions


def _add_memory(assistant, tag_names):
    entry = MemoryEntry.objects.create(event="e", assistant=assistant)
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name, slug=name)
        entry.tags.add(tag)


def test_collision_same_archetype(db):
    a1 = Assistant.objects.create(name="A1", specialty="test", archetype_path="hero")
    a2 = Assistant.objects.create(name="A2", specialty="test", archetype_path="hero")

    _add_memory(a1, ["quest"])
    _add_memory(a2, ["quest"])

    results = detect_role_collisions()
    assert len(results) == 1
    assert results[0]["proposal"].startswith("merge")
    assert "quest" in results[0]["shared_tags"]


def test_collision_different_archetype(db):
    a1 = Assistant.objects.create(name="B1", specialty="s1", archetype_path="hero")
    a2 = Assistant.objects.create(name="B2", specialty="s2", archetype_path="villain")

    _add_memory(a1, ["lore"])
    _add_memory(a2, ["lore"])

    results = detect_role_collisions()
    assert any(r["proposal"].startswith("clarify") for r in results)

