import pytest

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant, AssistantTaskRunLog
from prompts.models import Prompt, PromptMutationLog
from memory.models import MemoryEntry
from metrics.models import TaskEvolutionSuggestion, PromptVersionTrace, SwarmTaskCluster
from learning_loops.models import SkillTrainingMap, MemorySkillAlignmentIndex, TrainingSuggestionFeedbackLog
from prompts.models import PromptFeedbackVector, PromptMutationEffectTrace


def test_phase_omega_6_2_models_create(db):
    client = Client()
    assistant = Assistant.objects.create(name="A", specialty="test")
    run = AssistantTaskRunLog.objects.create(assistant=assistant, task_text="t", result_text="r")
    prompt = Prompt.objects.create(title="p", content="c", source="s")
    memory = MemoryEntry.objects.create(event="e", assistant=assistant)

    sugg = TaskEvolutionSuggestion.objects.create(run_log=run, suggestion_text="improve")
    trace = PromptVersionTrace.objects.create(prompt=prompt, feedback_score=0.8)
    cluster = SwarmTaskCluster.objects.create(name="c")
    cluster.tasks.add(run)

    map_item = SkillTrainingMap.objects.create(assistant=assistant, skill_name="focus")
    align = MemorySkillAlignmentIndex.objects.create(memory=memory, skill="focus", coverage_score=0.5)
    feed_log = TrainingSuggestionFeedbackLog.objects.create(assistant=assistant, suggestion="try")

    vec = PromptFeedbackVector.objects.create(prompt=prompt, feedback_score=0.9)
    mutation = PromptMutationLog.objects.create(original_prompt=prompt, mutated_text="m", mode="t")
    effect = PromptMutationEffectTrace.objects.create(mutation=mutation, feedback_vector=vec)

    assert sugg.run_log == run
    assert trace.prompt == prompt
    assert cluster.tasks.count() == 1
    assert map_item.skill_name == "focus"
    assert align.memory == memory
    assert not feed_log.applied
    assert effect.feedback_vector == vec

    resp1 = client.get("/api/metrics/evolve/swarm/")
    assert resp1.status_code == 200
    resp2 = client.get(f"/api/feedback/prompts/{prompt.id}/")
    assert resp2.status_code == 200
    resp3 = client.get(f"/api/plan/skills/{assistant.id}/")
    assert resp3.status_code == 200
