from assistants.models import Assistant
from mcp_core.models import PublicEventLog
from django.utils import timezone
from utils import is_valid_uuid
from utils.resolvers import resolve_or_error


def resolve_assistant(identifier):
    """Return assistant by id, slug, or memory_context_id."""
    if not identifier:
        return None

    try:
        return resolve_or_error(identifier, Assistant)
    except Exception:
        pass

    return Assistant.objects.filter(memory_context_id=identifier).first()


def log_cli_assistant_event(
    command_name: str, assistant: Assistant, auto_created: bool
):
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
