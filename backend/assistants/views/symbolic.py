from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agents.models.identity import PersonalCodexAnchor
from agents.models.lore import BeliefForkEvent
from agents.serializers import CodexAnchorSerializer, BeliefForkEventSerializer


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


class CodexAnchorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        anchors = PersonalCodexAnchor.objects.filter(codex__created_by__slug=slug).order_by(
            "-created_at"
        )
        serializer = CodexAnchorSerializer(anchors, many=True)
        return Response(serializer.data)


class BeliefForkListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        forks = BeliefForkEvent.objects.filter(originating_assistant__slug=slug).order_by(
            "-created_at"
        )
        serializer = BeliefForkEventSerializer(forks, many=True)
        return Response(serializer.data)
