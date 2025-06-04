from typing import Dict, List
from assistants.models import AssistantBootLog
from django.urls import get_resolver
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.project import AssistantProject
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from capabilities.registry import CAPABILITY_REGISTRY
from capabilities.models import CapabilityUsageLog


def generate_boot_profile(assistant: Assistant) -> Dict[str, object]:
    """Return a boot diagnostics profile for ``assistant``."""
    resolver = get_resolver()
    all_urls = []
    for p in resolver.url_patterns:
        all_urls.append(str(p.pattern))

    capabilities: List[Dict[str, object]] = []
    cap_data = assistant.capabilities_dict()

    for key, info in CAPABILITY_REGISTRY.items():
        route = info.get("route", "")
        connected = any(u.startswith(route.lstrip("/")) for u in all_urls)
        enabled = bool(cap_data.get(key))
        last_used = (
            CapabilityUsageLog.objects.filter(assistant=assistant, capability=key)
            .order_by("-created_at")
            .values_list("created_at", flat=True)
            .first()
        )
        capabilities.append(
            {
                "key": key,
                "enabled": enabled,
                "connected": connected,
                "last_used": last_used,
            }
        )

    prompt = assistant.system_prompt
    anchors_total = SymbolicMemoryAnchor.objects.count()
    anchors_linked = (
        SymbolicMemoryAnchor.objects.filter(chunks__isnull=False).distinct().count()
    )
    anchors_active = (
        SymbolicMemoryAnchor.objects.filter(memories__assistant=assistant)
        .distinct()
        .count()
    )
    reflections_total = AssistantReflectionLog.objects.filter(assistant=assistant).count()
    projects_total = AssistantProject.objects.filter(assistant=assistant).count()
    last_log = (
        AssistantBootLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .first()
    )

    return {
        "assistant_id": str(assistant.id),
        "system_prompt": {
            "title": prompt.title if prompt else None,
            "token_count": prompt.token_count if prompt else 0,
        },
        "capabilities": capabilities,
        "glossary_anchors": {
            "total": anchors_total,
            "linked": anchors_linked,
            "active": anchors_active,
        },
        "reflections_total": reflections_total,
        "projects_total": projects_total,
        "last_boot":
            {
                "passed": last_log.passed,
                "timestamp": last_log.created_at.isoformat(),
            }
            if last_log
            else None,
    }


def run_assistant_self_test(assistant: Assistant) -> Dict[str, object]:
    """Run a lightweight self-test on ``assistant`` and return results."""
    issues: List[str] = []

    if not assistant.system_prompt:
        issues.append("prompt_not_assigned")

    if not assistant.documents.exists():
        issues.append("no_documents")

    if not MemoryEntry.objects.filter(assistant=assistant).exists():
        issues.append("no_memory")

    if not AssistantReflectionLog.objects.filter(assistant=assistant).exists():
        issues.append("no_reflections")

    passed = len(issues) == 0
    return {"passed": passed, "issues": issues}
