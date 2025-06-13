from assistants.models import Assistant
from mcp_core.models import PublicEventLog
from django.utils import timezone
from utils import is_valid_uuid


def resolve_assistant(identifier):
    """Return assistant by id, slug, or memory_context_id."""
    if not identifier:
        return None

    if is_valid_uuid(identifier):
        found = Assistant.objects.filter(id=identifier).first()
        if found:
            return found

    found = Assistant.objects.filter(slug=identifier).first()
    if found:
        return found

    return Assistant.objects.filter(memory_context_id=identifier).first()


def log_cli_assistant_event(command_name: str, assistant: Assistant, auto_created: bool):
    """Record a CLI assistant event in PublicEventLog."""
    details = (
        f"command={command_name} slug={assistant.slug} id={assistant.id} "
        f"auto_created={auto_created}"
    )
    PublicEventLog.objects.create(
        actor_name="cli",
        event_details=details,
        timestamp=timezone.now(),
    )
