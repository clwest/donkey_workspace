from assistants.models.reflection import AssistantReflectionLog
from assistants.models.project import AssistantObjective
from assistants.helpers.logging_helper import log_assistant_thought
from prompts.utils.openai_utils import complete_chat


def generate_objective_from_reflection(
    reflection: AssistantReflectionLog,
) -> AssistantObjective:
    """Generate a project objective based on a reflection."""
    system = "You summarize reflections into concise project objectives."
    user = (
        f"Reflection summary:\n{reflection.summary}\n\n"
        "Return one objective in the format: Title: Description"
    )
    result = complete_chat(system=system, user=user)
    if ":" in result:
        title, desc = result.split(":", 1)
    else:
        title, desc = result.strip(), ""
    objective = AssistantObjective.objects.create(
        assistant=reflection.assistant,
        project=reflection.project,
        title=title.strip(),
        description=desc.strip(),
        generated_from_reflection=reflection,
        source_memory=reflection.linked_memory,
    )

    log_assistant_thought(
        reflection.assistant,
        "objective evolved",
        project=reflection.project,
        linked_reflection=reflection,
        thought_type="planning",
    )

    return objective
