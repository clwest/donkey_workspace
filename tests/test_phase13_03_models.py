import pytest

pytest.importorskip("django")

from assistants.models import Assistant, AssistantDashboardNotification, CodexStateAlert, RitualStatusBeacon
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    CodexContributionCeremony,
    DirectiveMemoryNode,
    EncodedRitualBlueprint,
    RitualArchiveEntry,
)
from metrics.models import RitualPerformanceMetric


def test_phase13_03_models_create(db):
    assistant = Assistant.objects.create(name="A")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    ceremony = CodexContributionCeremony.objects.create(
        ceremony_title="Cer", contributor_id="u1", symbolic_proposal="p", codex_target=codex
    )
    directive = DirectiveMemoryNode.objects.create(
        assistant=assistant,
        purpose_statement="p",
        triggering_conditions={},
        directive_tags={},
        temporal_scope="t",
    )
    archive = RitualArchiveEntry.objects.create(
        name="R", ceremony_type="type", symbolic_impact_summary="s"
    )
    archive.participant_assistants.add(assistant)
    ritual_metric = RitualPerformanceMetric.objects.create(
        ritual=archive,
        assistant=assistant,
        symbolic_score=0.5,
        transformation_alignment=0.5,
        mythic_tags={},
        reflection_notes="n",
    )
    blueprint = EncodedRitualBlueprint.objects.create(name="B", encoded_steps={})

    notif = AssistantDashboardNotification.objects.create(
        assistant=assistant,
        alert_type="Ritual Ready",
        message="m",
        related_memory=memory,
        related_ceremony=ceremony,
        related_directive=directive,
        related_metric=ritual_metric,
    )
    alert = CodexStateAlert.objects.create(
        codex=codex, entropy_level=0.5, coherence_index=0.8, alignment_drift=0.1
    )
    beacon = RitualStatusBeacon.objects.create(
        assistant=assistant,
        ritual_blueprint=blueprint,
        availability_state="ready",
        entropy_level=0.2,
        alignment_readiness=0.9,
    )

    assert notif.related_memory == memory
    assert alert.codex == codex
    assert beacon.ritual_blueprint == blueprint
