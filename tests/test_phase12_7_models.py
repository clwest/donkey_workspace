import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    SymbolicDocumentationEntry,
    CodexReconciliationForum,
    MythEditorialLayer,
    SymbolicPublishingEngine,
)


def test_phase12_7_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="d")
    doc = SymbolicDocumentationEntry.objects.create(title="T", content="x", created_by=assistant)

    forum = CodexReconciliationForum.objects.create(
        forum_topic="topic",
        reconciliation_log="log",
        resolution_achieved=True,
    )
    forum.initiating_codices.add(codex)
    forum.participating_assistants.add(assistant)
    forum.memory_basis.add(mem)

    layer = MythEditorialLayer.objects.create(
        linked_entry=doc,
        suggested_edits={},
        commentary_threads={},
        editorial_tags={},
    )

    engine = SymbolicPublishingEngine.objects.create(
        published_title="pub",
        content_type="ritual",
        publishing_entity="entity",
        visibility_scope="swarm",
        symbolic_payload={},
    )
    engine.approved_codexes.add(codex)

    assert forum.initiating_codices.count() == 1
    assert layer.linked_entry == doc
    assert engine.approved_codexes.count() == 1
