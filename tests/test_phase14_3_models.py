from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    RitualEchoThreadSystem,
    CodexRecurrenceLoopEngine,
    CycleAnchorRegistry,
    MemoryRegenerationProtocol,
    RitualLoopVisualizationEngine,
    SymbolicOscillationMap,
    CodexRestabilizationNode,
)
from metrics.models import RitualPerformanceMetric
from agents.models.lore import RitualArchiveEntry
from agents.models.coordination import DirectiveMemoryNode


def test_phase14_3_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")
    ritual = RitualArchiveEntry.objects.create(
        name="R",
        ceremony_type="init",
        symbolic_impact_summary="s",
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
    echo = RitualEchoThreadSystem.objects.create(
        ritual_metric=metric,
        memory_entry=memory,
        codex=codex,
        echo_pattern={"e": 1},
        echo_intensity=0.8,
        assistant_history=[assistant.id],
    )
    anchor = CycleAnchorRegistry.objects.create(
        assistant=assistant,
        anchor_name="A1",
        role_trait_snapshot={"r": 1},
        symbolic_notes="n",
    )
    directive = DirectiveMemoryNode.objects.create(
        assistant=assistant,
        purpose_statement="p",
        triggering_conditions={"c": 1},
        directive_tags={"d": 1},
        temporal_scope="t",
    )
    recurrence = CodexRecurrenceLoopEngine.objects.create(
        codex=codex,
        cycle_trigger_points={"p": 1},
        mutation_path_log="log",
        symbolic_phase_tags=["alpha"],
        renewal_recommendation="keep",
    )
    protocol = MemoryRegenerationProtocol.objects.create(
        assistant=assistant,
        trigger_codex=codex,
        regeneration_script="s",
        symbolic_success_score=0.5,
    )
    protocol.corrupted_memory_nodes.add(memory)
    loop = RitualLoopVisualizationEngine.objects.create(
        ritual_metric=metric,
        anchor_registry=anchor,
        echo_thread=echo,
        loop_map={"l": 1},
        frequency_trails={"f": 1},
        convergence_points={"c": 1},
    )
    osc = SymbolicOscillationMap.objects.create(
        codex_engine=recurrence,
        directive_node=directive,
        belief_drift_waveforms={"w": 1},
        codex_strain=0.9,
        role_pressure=0.7,
    )
    node = CodexRestabilizationNode.objects.create(
        assistant=assistant,
        codex=codex,
        symbolic_disruption_score=0.8,
        stabilizing_action="a",
        restoration_tags={"tag": 1},
    )

    assert loop.echo_thread == echo
    assert osc.directive_node == directive
    assert node.codex == codex
