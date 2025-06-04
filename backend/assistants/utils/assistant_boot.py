import json
from typing import List, Dict

from assistants.models import Assistant, AssistantBootLog
from .boot_diagnostics import generate_boot_profile, run_assistant_self_test


def run_batch_self_tests() -> List[Dict[str, object]]:
    """Run boot diagnostics for all assistants."""

    results = []
    for assistant in Assistant.objects.all():
        generate_boot_profile(assistant)
        result = run_assistant_self_test(assistant)
        log = AssistantBootLog.objects.create(
            assistant=assistant, passed=result["passed"], report=json.dumps(result)
        )
        results.append(
            {
                "assistant": assistant.slug,
                "passed": result["passed"],
                "issues": result.get("issues", []),
                "timestamp": log.created_at.isoformat(),
            }
        )
    return results
