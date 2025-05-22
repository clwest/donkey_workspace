from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from assistants.models import PurposeRouteMap, AutonomyNarrativeModel
from assistants.serializers import (
    PurposeRouteMapSerializer,
    AutonomyNarrativeModelSerializer,
)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def purpose_routes(request):
    if request.method == "GET":
        routes = PurposeRouteMap.objects.all().order_by("-created_at")
        return Response(PurposeRouteMapSerializer(routes, many=True).data)

    serializer = PurposeRouteMapSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    route = serializer.save()
    return Response(PurposeRouteMapSerializer(route).data, status=201)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def autonomy_models(request):
    if request.method == "GET":
        models = AutonomyNarrativeModel.objects.all().order_by("-created_at")
        return Response(AutonomyNarrativeModelSerializer(models, many=True).data)

    serializer = AutonomyNarrativeModelSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    model = serializer.save()
    return Response(AutonomyNarrativeModelSerializer(model).data, status=201)
