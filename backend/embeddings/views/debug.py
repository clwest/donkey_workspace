from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.utils import timezone

from embeddings.utils.link_repair import repair_context_embeddings
from embeddings.models import EmbeddingDriftLog
from memory.models import MemoryEntry

@api_view(["POST"])
@permission_classes([IsAdminUser])
def repair_context(request, context_id):
    """Repair embeddings for a specific MemoryContext."""
    result = repair_context_embeddings(context_id)
    mem = MemoryEntry.objects.filter(context_id=context_id).first()
    EmbeddingDriftLog.objects.create(
        model_name="memoryentry",
        assistant=mem.assistant if mem else None,
        context_id=context_id,
        mismatched_count=result["scanned"] - result["fixed"],
        orphaned_count=0,
        repaired_count=result["fixed"],
        repair_attempted_at=timezone.now(),
        repair_success_count=result["fixed"],
        repair_failure_count=result["scanned"] - result["fixed"],
    )
    return Response(result)
