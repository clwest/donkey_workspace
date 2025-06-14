import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from unittest.mock import patch
import pytest

from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from assistants.utils.trust_profile import get_cached_trust

pytest.importorskip("django")


@pytest.mark.django_db
def test_refresh_trust_profile_cli():
    a = Assistant.objects.create(name="T", slug="t")
    with patch("assistants.utils.trust_profile.compute_trust_score") as mock:
        mock.return_value = {"score": 42, "level": "training", "components": {}}
        call_command("refresh_trust_profile", "--assistant", a.slug)
    a.refresh_from_db()
    assert a.last_trust_score == 42
    cached = get_cached_trust(a.slug)
    assert cached and cached["score"] == 42


@pytest.mark.django_db
def test_patch_growth_state_cli():
    a = Assistant.objects.create(name="G", slug="g", nurture_started_at=django.utils.timezone.now())
    AssistantDiagnosticReport.objects.create(
        assistant=a,
        slug="g",
        fallback_rate=0.0,
        glossary_success_rate=1.0,
        avg_chunk_score=1.0,
        rag_logs_count=5,
    )
    with patch("assistants.utils.trust_profile.compute_trust_score") as mock:
        mock.return_value = {"score": 60, "level": "ready", "components": {}}
        call_command("patch_growth_state", "--assistant", a.slug)
    a.refresh_from_db()
    assert a.growth_points > 0
    assert a.growth_stage >= 1


@pytest.mark.django_db
def test_retry_doc_reflections_cli():
    from intel_core.models import Document

    doc = Document.objects.create(title="D", content="x")
    with patch(
        "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.reflect_on_document"
    ) as mock:
        mock.return_value = ("sum", [], None)
        call_command("retry_doc_reflections")
    mock.assert_called()

