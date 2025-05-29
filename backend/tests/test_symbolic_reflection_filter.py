import pytest
pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant
from memory.models import MemoryEntry


def test_symbolic_reflection_filter(db):
    client = Client()
    assistant = Assistant.objects.create(name="A")
    m1 = MemoryEntry.objects.create(event="one", assistant=assistant)
    m2 = MemoryEntry.objects.create(event="two", assistant=assistant, symbolic_change=True)

    resp = client.get("/api/memory/list/", {"assistant_id": assistant.id, "symbolic_change": "true"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(m2.id)
