import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, SwarmCodex
from agents.models.storyfield import (
    PlotlineExtractorEngine,
    MemoryCompressionRitualTool,
    CodexStoryReshaper,
)


def test_phase13_8_models_create(db):
    assistant = Assistant.objects.create(name="Beta", specialty="bard")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="myth")
    memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    extractor = PlotlineExtractorEngine.objects.create(
        assistant=assistant,
        archetype_tags=["hero"],
        codex_influence_map={"c": 1},
        symbolic_plot_summary="sum",
    )
    extractor.input_memory_set.add(memory)

    tool = MemoryCompressionRitualTool.objects.create(
        initiating_assistant=assistant,
        ritual_script="r",
        compressed_summary="s",
        aura_score=0.5,
    )
    tool.source_entries.add(memory)

    reshaper = CodexStoryReshaper.objects.create(
        reshaper_title="R",
        initiating_assistant=assistant,
        target_codex=codex,
        belief_shift_map={"b": 1},
        ritual_reorder_log={"r": 1},
    )

    assert extractor.input_memory_set.count() == 1
    assert tool.source_entries.count() == 1
    assert reshaper.target_codex == codex
