import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from unittest.mock import patch
import pytest
from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog, AnchorDriftLog


@pytest.mark.django_db
@patch(
    "memory.management.commands.track_anchor_drift.suggest_mutation_with_rationale",
    return_value=("new", "r"),
)
@patch("memory.management.commands.track_anchor_drift.reflect_on_anchor_drift")
def test_track_anchor_drift_creates_log(mock_reflect, mock_suggest):
    a = Assistant.objects.create(name="A", slug="a")
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="term", label="Term", memory_context=a.memory_context
    )
    for i in range(3):
        RAGGroundingLog.objects.create(
            assistant=a,
            query="q",
            used_chunk_ids=["1"],
            expected_anchor="term",
            adjusted_score=1.0 - i * 0.3,
        )
    call_command("track_anchor_drift", "--assistant", "a", "--log")
    anchor.refresh_from_db()
    assert anchor.suggested_label == "new"
    assert AnchorDriftLog.objects.filter(anchor=anchor).count() == 1
    mock_reflect.assert_called_once()
