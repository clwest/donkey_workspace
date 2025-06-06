from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from assistants.utils.onboarding_tracker import record_step_completion, get_onboarding_status


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def onboarding_status(request):
    progress = get_onboarding_status(request.user)
    return Response({"progress": progress})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def onboarding_complete(request):
    step = request.data.get("step")
    if not step:
        return Response({"error": "step required"}, status=400)
    record_step_completion(request.user, step)
    progress = get_onboarding_status(request.user)
    return Response({"progress": progress})
