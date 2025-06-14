import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.core.management import call_command
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor, RAGPlaybackLog
import pytest

pytest.importorskip("django")


@pytest.mark.django_db
def test_rebuild_anchors_cli_creates_anchor_for_assistant():
    a = Assistant.objects.create(name="Godel", slug="godelbot")
    doc = Document.objects.create(title="D", content="t")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="zk rollup improves scalability",
        tokens=5,
        fingerprint="f1",
    )
    RAGPlaybackLog.objects.create(
        assistant=a,
        query="what is zk rollup",
        memory_context=None,
        chunks=[{"id": str(chunk.id), "final_score": 0.6}],
    )

    call_command(
        "rebuild_anchors_from_chunks",
        "--assistant",
        a.slug,
        "--threshold",
        "0.4",
    )

    assert SymbolicMemoryAnchor.objects.filter(slug="zk-rollup", assistant=a).exists()


@pytest.mark.django_db
def test_rebuild_anchors_cli_all_context():
    a1 = Assistant.objects.create(name="A1", slug="a1")
    a2 = Assistant.objects.create(name="A2", slug="a2")
    doc = Document.objects.create(title="D2", content="t")
    chunk = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="smart contract deployment",
        tokens=4,
        fingerprint="f2",
    )
    RAGPlaybackLog.objects.create(
        assistant=a1,
        query="deploy",
        memory_context=None,
        chunks=[{"id": str(chunk.id), "final_score": 0.6}],
    )
    RAGPlaybackLog.objects.create(
        assistant=a2,
        query="deploy",
        memory_context=None,
        chunks=[{"id": str(chunk.id), "final_score": 0.6}],
    )

    call_command("rebuild_anchors_from_chunks", "--threshold", "0.4")

    assert SymbolicMemoryAnchor.objects.filter(slug="smart-contract").count() == 1
