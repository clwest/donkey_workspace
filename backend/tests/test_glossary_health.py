import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog
from assistants.serializers import AssistantSerializer

@pytest.mark.django_db
def test_glossary_health_index():
    a = Assistant.objects.create(name="A")
    anchor = SymbolicMemoryAnchor.objects.create(slug="evm", label="evm")
    anchor.reinforced_by.add(a)
    for _ in range(3):
        RAGGroundingLog.objects.create(
            assistant=a,
            fallback_triggered=True,
            expected_anchor="evm",
            adjusted_score=0.05,
        )
    data = AssistantSerializer(a).data
    assert data["glossary_health_index"] == 0.0
