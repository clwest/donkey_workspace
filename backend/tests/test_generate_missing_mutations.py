import pytest
from unittest.mock import patch

pytest.importorskip("django")

from django.core.management import call_command
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import GlossaryFallbackReflectionLog


@patch("utils.llm.call_gpt4", return_value="better term")
@pytest.mark.django_db
def test_generate_missing_mutations_command(mock_call):
    a = Assistant.objects.create(name="Clar", slug="claritybot")
    anchor = SymbolicMemoryAnchor.objects.create(
        slug="foo",
        label="foo",
        mutation_status="pending",
        assistant=a,
        fallback_score=0.2,
    )
    for _ in range(3):
        GlossaryFallbackReflectionLog.objects.create(
            anchor_slug="foo",
            chunk_id="c",
            match_score=0.05,
            assistant_response="no",
            glossary_injected=True,
        )

    call_command("generate_missing_mutations", "--assistant", "claritybot")

    anchor.refresh_from_db()
    assert anchor.suggested_label == "better term"
    mock_call.assert_called_once()
