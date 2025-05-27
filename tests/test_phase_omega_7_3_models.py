import pytest

pytest.importorskip("django")

from assistants.models import Assistant, AssistantReflectionLog
from prompts.models import Prompt, PromptMutationLog
from prompts.utils.mutation import mutate_prompt_from_reflection


def test_phase_omega_7_3_models_prompt_mutation(db):
    assistant = Assistant.objects.create(name="A", specialty="sage")
    prompt = Prompt.objects.create(title="P", content="base", source="s")
    assistant.system_prompt = prompt
    assistant.save()

    reflection = AssistantReflectionLog.objects.create(
        assistant=assistant, title="fail", summary="could not answer"
    )
    new_prompt = mutate_prompt_from_reflection(
        assistant, reflection_log=reflection, reason="test"
    )

    mutation = PromptMutationLog.objects.get(triggered_by_reflection=reflection)
    assert mutation.assistant == assistant
    assert mutation.source_prompt == prompt
    assert mutation.mutated_prompt == new_prompt
    assert assistant.system_prompt == new_prompt
