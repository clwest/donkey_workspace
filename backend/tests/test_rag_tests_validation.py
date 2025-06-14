import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from io import StringIO
from assistants.models import Assistant
import json
import pytest

pytest.importorskip("django")


@pytest.mark.django_db
def test_rag_tests_file_assistant_mismatch(tmp_path):
    a1 = Assistant.objects.create(name="A1", slug="a1")
    a2 = Assistant.objects.create(name="A2", slug="a2")
    path = tmp_path / "rag.json"
    with open(path, "w") as f:
        json.dump({"assistant": a2.slug, "tests": []}, f)
    buf = StringIO()
    call_command(
        "run_rag_tests", "--assistant", a1.slug, "--file", str(path), stdout=buf
    )
    assert "rag_tests.json is for assistant" in buf.getvalue()


@pytest.mark.django_db
def test_rag_tests_unknown_anchor(tmp_path):
    a = Assistant.objects.create(name="A", slug="a")
    path = tmp_path / "rag.json"
    with open(path, "w") as f:
        json.dump({"tests": [{"question": "q", "expected_anchor": "missing"}]}, f)
    buf = StringIO()
    call_command(
        "run_rag_tests", "--assistant", a.slug, "--file", str(path), stdout=buf
    )
    assert "Unknown anchor" in buf.getvalue()
