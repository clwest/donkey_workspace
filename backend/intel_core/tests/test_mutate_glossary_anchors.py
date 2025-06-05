import json
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("django")

from django.core.management import call_command
from assistants.models import Assistant
from memory.models import GlossaryChangeEvent


@patch(
    "intel_core.management.commands.mutate_glossary_anchors.suggest_anchor_mutations",
    return_value=(
        '1. "May 31, 2025" - This is a straightforward rephrasing using a more standard date format.\n'
        '2. "End of May 2025" - This phrase provides a broader time frame that still includes the specific date.'
    ),
)
@pytest.mark.django_db
def test_mutate_glossary_handles_long_lines(mock_suggest, tmp_path):
    assistant = Assistant.objects.create(name="Clar", slug="clar")
    data = [{"assistant": assistant.slug, "issues": ["2025-05-31"]}]
    json_path = tmp_path / "diag.json"
    json_path.write_text(json.dumps(data))

    call_command(
        "mutate_glossary_anchors",
        "--assistant",
        assistant.slug,
        "--from-json",
        str(json_path),
        "--save-to-review",
    )

    event = GlossaryChangeEvent.objects.get()
    assert event.term == "May 31, 2025"
