import logging
from .models import CapabilityUsageLog
from assistants.models.assistant import Assistant

logger = logging.getLogger(__name__)


def log_capability_usage(request, capability: str):
    """Record usage of a capability. Failure is non-fatal."""
    assistant = None
    slug = request.GET.get("slug") or request.data.get("slug") if hasattr(request, "data") else None
    if slug:
        assistant = Assistant.objects.filter(slug=slug).first()
    try:
        CapabilityUsageLog.objects.create(
            assistant=assistant,
            capability=capability,
            request_path=request.path,
        )
    except Exception as exc:
        logger.error("Failed to log capability usage: %s", exc, exc_info=True)

