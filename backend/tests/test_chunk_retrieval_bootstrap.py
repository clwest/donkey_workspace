import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest
from django.core.management import call_command
from assistants.utils.chunk_retriever import get_relevant_chunks
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from assistants.models import Assistant

pytest.importorskip("django")


@pytest.mark.django_db
def test_chunk_retrieval_works_for_bootstrapped_assistants():
    assistant = Assistant.objects.create(name="Boot", slug="boot")
    doc = Document.objects.create(title="Guide", content="the purpose is testing")
    assistant.documents.add(doc)
    doc.memory_context = assistant.memory_context
    doc.save(update_fields=["memory_context"])
    emb = EmbeddingMetadata.objects.create(model_used="m", num_tokens=1, vector=[0.1])
    DocumentChunk.objects.create(
        document=doc,
        order=1,
        text="The purpose of the assistant is to help",
        tokens=5,
        fingerprint="fp1",
        embedding=emb,
        embedding_status="embedded",
    )

    chunks, *_ = get_relevant_chunks(str(assistant.id), "purpose")
    assert chunks
