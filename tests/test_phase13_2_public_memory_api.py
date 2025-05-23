import pytest

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant, MythCommunityCluster
from agents.models import SwarmCodex, SwarmMemoryEntry, PublicMemoryGrove


def test_public_memory_grove_api(db):
    client = Client()
    assistant = Assistant.objects.create(name="A")
    codex = SwarmCodex.objects.create(
        title="C", created_by=assistant, symbolic_domain="myth"
    )
    memory = SwarmMemoryEntry.objects.create(title="m", content="c")
    cluster = MythCommunityCluster.objects.create(cluster_name="core")
    grove = PublicMemoryGrove.objects.create(
        grove_name="G1",
        linked_cluster=cluster,
        codex_reference=codex,
    )
    grove.featured_memories.add(memory)

    resp = client.get("/api/memory/grove/public/", {"codex": codex.id})
    assert resp.status_code == 200
    data = resp.json()
    assert data and data[0]["memory_count"] == 1
