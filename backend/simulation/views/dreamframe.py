from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import DreamframeStoryGenerator, SimScenarioEngine, MultiUserNarrativeLab
from ..serializers import (
    DreamframeStoryGeneratorSerializer,
    SimScenarioEngineSerializer,
    MultiUserNarrativeLabSerializer,
)


class DreamframeStoryGeneratorViewSet(viewsets.ModelViewSet):
    queryset = DreamframeStoryGenerator.objects.all().order_by("-created_at")
    serializer_class = DreamframeStoryGeneratorSerializer


class SimScenarioEngineViewSet(viewsets.ModelViewSet):
    queryset = SimScenarioEngine.objects.all().order_by("-created_at")
    serializer_class = SimScenarioEngineSerializer


class MultiUserNarrativeLabViewSet(viewsets.ModelViewSet):
    queryset = MultiUserNarrativeLab.objects.all().order_by("-created_at")
    serializer_class = MultiUserNarrativeLabSerializer


@api_view(["GET"])
def dreamframe_generate(request):
    """Launch or customize symbolic story scripts."""
    generators = DreamframeStoryGenerator.objects.all().order_by("-created_at")
    serializer = DreamframeStoryGeneratorSerializer(generators, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def scenario_play(request):
    """Play through codex-aligned ritualized simulations."""
    scenarios = SimScenarioEngine.objects.all().order_by("-created_at")
    serializer = SimScenarioEngineSerializer(scenarios, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def narrative_lab(request):
    """Co-create stories in shared belief design labs."""
    labs = MultiUserNarrativeLab.objects.all().order_by("-created_at")
    serializer = MultiUserNarrativeLabSerializer(labs, many=True)
    return Response(serializer.data)

