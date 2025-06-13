import uuid
from typing import Optional
from .logging_utils import get_logger

logger = get_logger(__name__)


def coerce_uuid(value, field_name: str = "unknown") -> Optional[uuid.UUID]:
    """Attempt to convert ``value`` to a :class:`uuid.UUID`.

    If ``value`` is not a valid UUID, a warning is logged and ``None`` is
    returned.
    """
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        logger.warning(f"[UUID Sanity] Invalid UUID format for {field_name}: {value}")
        return None


def is_valid_uuid(value: str) -> bool:
    """Return ``True`` if ``value`` is a valid UUID string."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False
