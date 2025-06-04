from typing import Dict, List

from django.utils.timezone import now

from assistants.models import Assistant, AssistantBootLog


def generate_boot_profile(assistant: Assistant) -> Dict[str, object]:
    """Return a simplified boot profile for ``assistant``."""
    last_log = (
        AssistantBootLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .first()
    )
    return {
        "has_system_prompt": bool(assistant.system_prompt),
        "has_memory_context": bool(assistant.memory_context),
        "has_preferred_model": bool(assistant.preferred_model),
        "last_tested_at": last_log.created_at if last_log else None,
    }


def run_assistant_self_test(assistant: Assistant) -> Dict[str, object]:
    """Run a basic self-test for ``assistant`` and record the result."""
    profile = generate_boot_profile(assistant)
    errors: List[str] = []

    if not profile["has_system_prompt"]:
        errors.append("Missing system prompt")
    if not profile["has_memory_context"]:
        errors.append("Missing memory context")
    if not profile["has_preferred_model"]:
        errors.append("Missing preferred model")

    passed = len(errors) == 0

    AssistantBootLog.objects.create(
        assistant=assistant,
        passed=passed,
        report="\n".join(errors),
    )

    return {"assistant": assistant.slug, "passed": passed, "errors": errors}


def run_batch_self_tests() -> List[Dict[str, object]]:
    """Run self-tests for all assistants and return their results."""
    results: List[Dict[str, object]] = []
    for a in Assistant.objects.all():
        results.append(run_assistant_self_test(a))
    return results
