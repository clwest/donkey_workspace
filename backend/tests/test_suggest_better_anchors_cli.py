import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.core.management import call_command
from io import StringIO
import pytest

from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog

pytest.importorskip("django")


@pytest.mark.django_db
def test_suggest_better_anchors_creates_anchor():
    a = Assistant.objects.create(name="A", slug="a")
    doc = Document.objects.create(title="Doc", content="t")
    c1 = DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="random words",
        tokens=2,
        fingerprint="f1",
        score=0.1,
    )
    c2 = DocumentChunk.objects.create(
        document=doc,
        order=2,
        text="quantum flux engine",
        tokens=3,
        fingerprint="f2",
        score=0.9,
    )
    RAGGroundingLog.objects.create(
        assistant=a,
        query="q",
        used_chunk_ids=[str(c1.id)],
        fallback_triggered=True,
        adjusted_score=0.1,
    )

    out = StringIO()
    call_command(
        "suggest_better_anchors",
        "--assistant",
        a.slug,
        "--auto-approve",
        stdout=out,
    )

    assert SymbolicMemoryAnchor.objects.filter(slug="quantum", assistant=a).exists()
