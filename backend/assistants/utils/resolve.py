from assistants.models import Assistant
from utils.resolvers import resolve_or_error


def resolve_assistant(value: str):
    """Return ``Assistant`` by UUID or slug, or ``None`` if not found."""
    try:
        return resolve_or_error(value, Assistant)
    except Exception:
        return None
