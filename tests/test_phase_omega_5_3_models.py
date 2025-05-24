import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from assistants.models.tasks import AssistantExecutionChain, ChainNodeMap
from prompts.models import Prompt
from tools.models import Tool
from agents.models.forecast import BeliefForecastSnapshot, CodexResonanceIndex
from agents.models.lore import SwarmCodex
from memory.models import MemoryEntry, MemoryEntropyAudit, MemoryMergeSuggestion


def test_phase_omega_5_3_models_create(db):
    assistant = Assistant.objects.create(name="Alpha", specialty="seer")
    codex = SwarmCodex.objects.create(title="C", created_by=assistant, symbolic_domain="core")
    prompt = Prompt.objects.create(title="P", content="x", created_by=assistant)
    tool = Tool.objects.create(name="T", slug="t", module_path="m", function_name="f")

    chain = AssistantExecutionChain.objects.create(title="Chain", created_by=assistant)
    node = ChainNodeMap.objects.create(chain=chain, step_order=1, assistant=assistant, prompt=prompt, tool=tool)

    snapshot = BeliefForecastSnapshot.objects.create(
        assistant=assistant,
        prompt=prompt,
        belief_alignment_score=0.8,
        drift_probability=0.2,
    )
    index = CodexResonanceIndex.objects.create(codex=codex, assistant=assistant, resonance_score=0.7)

    entry_a = MemoryEntry.objects.create(event="A")
    entry_b = MemoryEntry.objects.create(event="B")
    audit = MemoryEntropyAudit.objects.create(entropy_score=0.5)
    suggestion = MemoryMergeSuggestion.objects.create(entry_a=entry_a, entry_b=entry_b, merge_reason="dup")

    assert node.chain == chain
    assert snapshot.assistant == assistant
    assert index.codex == codex
    assert audit.entropy_score == 0.5
    assert suggestion.entry_a == entry_a
