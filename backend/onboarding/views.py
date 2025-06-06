from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .utils import (
    record_step_completion,
    get_onboarding_status,
    get_next_onboarding_step,
    get_progress_percent,
)
from .config import ONBOARDING_WORLD


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    return Response({"progress": progress, "next_step": next_step, "percent": percent})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def onboarding_complete(request):
    step = request.data.get("step")
    if not step:
        return Response({"error": "step required"}, status=400)
    record_step_completion(request.user, step)
    progress = get_onboarding_status(request.user)
    next_step = get_next_onboarding_step(request.user)
    percent = get_progress_percent(request.user)
    return Response({"progress": progress, "next_step": next_step, "percent": percent})


@api_view(["GET"])
@permission_classes([AllowAny])
def onboarding_node_detail(request, step):
    node = next((n for n in ONBOARDING_WORLD["nodes"] if n["slug"] == step), None)
    if not node:
        return Response({"error": "not found"}, status=404)
    return Response(node)
