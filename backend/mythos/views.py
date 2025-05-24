from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from agents.models.lore import SwarmCodex
from agents.serializers import SwarmCodexSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_archetype_card(request, assistant_id):
    """Return placeholder archetype card data for an assistant."""
    return Response({"tone": "", "tags": []})


@api_view(["GET"])
@permission_classes([AllowAny])
def get_ritual_launchpads(request):
    """Return placeholder ritual launchpad data."""
    return Response([])


class SwarmCodexRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        codices = SwarmCodex.objects.all().order_by("-created_at")
        serializer = SwarmCodexSerializer(codices, many=True)
        return Response(serializer.data)
