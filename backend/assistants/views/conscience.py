from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from assistants.models import Assistant, ConscienceModule, DecisionFramework
from assistants.serializers import (
    ConscienceModuleSerializer,
    DecisionFrameworkSerializer,
)
from assistants.utils.reflexive_epistemology import run_reflexive_belief_audit


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def conscience_profiles(request):
    if request.method == "GET":
        profiles = ConscienceModule.objects.all().order_by("-created_at")
        return Response(ConscienceModuleSerializer(profiles, many=True).data)

    serializer = ConscienceModuleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = serializer.save()
    return Response(ConscienceModuleSerializer(profile).data, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def reflexive_epistemology(request):
    slug = request.data.get("assistant")
    assistant = get_object_or_404(Assistant, slug=slug)
    result = run_reflexive_belief_audit(assistant)
    return Response(result)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def decision_frameworks(request):
    if request.method == "GET":
        decisions = DecisionFramework.objects.all().order_by("-created_at")
        return Response(DecisionFrameworkSerializer(decisions, many=True).data)

    serializer = DecisionFrameworkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    decision = serializer.save()
    return Response(DecisionFrameworkSerializer(decision).data, status=201)
