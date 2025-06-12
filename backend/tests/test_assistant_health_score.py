import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from prompts.models import Prompt
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from assistants.serializers_pass import AssistantSerializer

@pytest.mark.django_db
def test_composite_health_score():
    prompt = Prompt.objects.create(title="sys", type="system", content="hi", source="unit")
    assistant = Assistant.objects.create(
        name="A", specialty="test", mood_stability_index=0.8, system_prompt=prompt
    )
    doc = Document.objects.create(title="Doc", content="hi")
    assistant.documents.add(doc)

    DocumentChunk.objects.create(document=doc, order=1, text="a", tokens=1, fingerprint="f1")
    emb1 = EmbeddingMetadata.objects.create(model_used="x", num_tokens=1, vector=[0.0])
    DocumentChunk.objects.create(document=doc, order=2, text="b", tokens=1, fingerprint="f2", embedding=emb1, embedding_status="embedded")
    DocumentChunk.objects.create(document=doc, order=3, text="c", tokens=1, fingerprint="f3")
    emb2 = EmbeddingMetadata.objects.create(model_used="x", num_tokens=1, vector=[0.0])
    DocumentChunk.objects.create(document=doc, order=4, text="d", tokens=1, fingerprint="f4", embedding=emb2, embedding_status="embedded")

    data = AssistantSerializer(assistant).data
    assert data["health_score"] == 0.78
