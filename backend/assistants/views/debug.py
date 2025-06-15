from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count

from assistants.models import Assistant, AssistantReflectionLog
from memory.models import MemoryEntry
from utils.logging_utils import get_logger
from assistants.helpers.demo_utils import generate_demo_prompt_preview

logger = get_logger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def demo_checkup(request):
    """Return health overview for all demo assistants."""
    fix = str(request.query_params.get("fix", "")).lower() == "true"

    demos = Assistant.objects.filter(is_demo=True).annotate(
        memory_count=Count("memories")
    )

    results = []
    for a in demos:
        reflection_count = AssistantReflectionLog.objects.filter(assistant=a).count()
        starter_chat_count = (
            MemoryEntry.objects.filter(assistant=a, is_demo=True)
            .only("id", "created_at")
            .count()
        )
        has_prompt = bool(a.system_prompt)
        preview = a.system_prompt.content[:150] if a.system_prompt else ""
        if fix and not has_prompt:
            preview = generate_demo_prompt_preview(a)
            logger.info(
                "[demo_checkup] would generate prompt for %s: %s", a.slug, preview
            )
        results.append(
            {
                "slug": a.demo_slug or a.slug,
                "name": a.name,
                "has_system_prompt": has_prompt,
                "has_memory_context": bool(a.memory_context),
                "memory_count": a.memory_count,
                "reflection_count": reflection_count,
                "starter_chat_count": starter_chat_count,
                "prompt_preview": preview,
            }
        )
    return Response(results)
