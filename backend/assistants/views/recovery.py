from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import Assistant
from assistants.utils.recovery_engine import regenerate_assistant_plan


@api_view(["POST"])
@permission_classes([AllowAny])
def regenerate_plan(request, slug):
    """Regenerate an assistant's plan during recovery."""
    assistant = get_object_or_404(Assistant, slug=slug)

    if not assistant.needs_recovery:
        return Response({"error": "Assistant is not flagged for recovery"}, status=400)

    reason = request.data.get("recovery_reason")
    approve = bool(request.data.get("approve"))

    data = regenerate_assistant_plan(assistant, recovery_reason=reason)

    if approve:
        assistant.needs_recovery = False
        assistant.save(update_fields=["needs_recovery"])

    return Response(data)
