from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def get_codex_anchors(request, assistant_id):
    """Return placeholder codex anchor data."""
    return Response([])


@api_view(["GET"])
@permission_classes([AllowAny])
def get_belief_history(request, assistant_id):
    """Return placeholder belief history."""
    return Response([])


@api_view(["GET"])
@permission_classes([AllowAny])
def get_belief_forks(request, assistant_id):
    """Return placeholder belief forks."""
    return Response([])
