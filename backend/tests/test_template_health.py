import json
from pathlib import Path

import pytest

pytest.importorskip("django")

from django.core.management import call_command


def test_template_drift_detection(tmp_path, settings):
    template_file = tmp_path / "test.html"
    template_file.write_text("hello")

    settings.TEMPLATES[0]["DIRS"].append(str(tmp_path))

    call_command("validate_templates", "--only-folder", str(tmp_path))

    info_path = Path("logs/template_status.json")
    data = json.loads(info_path.read_text())
    assert str(template_file) in data

    # modify template to trigger drift
    template_file.write_text("hello world")

    out = call_command(
        "inspect_template_health",
        "--include-rag",
        stdout=None,
    )
    result = json.loads(out)
    status = next(
        item for item in result if item["template_path"] == str(template_file)
    )
    assert status["hash_diff"] is True
