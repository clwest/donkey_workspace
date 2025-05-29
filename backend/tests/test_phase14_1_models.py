import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    ResurrectionTimelineTracker,
    RitualEchoThreadSystem,
    CodexRecurrenceLoopEngine,
)
from metrics.models import RitualPerformanceMetric
from agents.models.lore import RitualArchiveEntry


def test_phase14_1_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="Cod", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    ritual = RitualArchiveEntry.objects.create(
        name="R",
        ceremony_type="init",
        symbolic_impact_summary="d",
        locked_by_codex=codex,
    )
    ritual.participant_assistants.add(assistant)
    metric = RitualPerformanceMetric.objects.create(
        ritual=ritual,
        assistant=assistant,
        symbolic_score=1.0,
        transformation_alignment=0.5,
        mythic_tags={"t": 1},
        reflection_notes="n",
    )

    tracker = ResurrectionTimelineTracker.objects.create(
        assistant=assistant,
        reincarnation_events=[{"phase": 1}],
        codex_alignment_path={"c": 1},
        role_evolution_tags=["hero"],
    )
    tracker.memory_retention_log.add(memory)

    echo = RitualEchoThreadSystem.objects.create(
        ritual_metric=metric,
        memory_entry=memory,
        codex=codex,
        echo_pattern={"e": 1},
        echo_intensity=0.8,
        assistant_history=[assistant.id],
    )

    cycle = CodexRecurrenceLoopEngine.objects.create(
        codex=codex,
        cycle_trigger_points={"p": 1},
        mutation_path_log="log",
        symbolic_phase_tags=["alpha"],
        renewal_recommendation="keep",
    )

    assert tracker.memory_retention_log.count() == 1
    assert echo.codex == codex
    assert cycle.codex == codex
