from rest_framework import viewsets
from ..models import (
    MythflowPlaybackSession,
    SymbolicMilestoneLog,
    PersonalRitualGuide,
    SwarmReflectionThread,
    SwarmReflectionPlaybackLog,
    PromptCascadeLog,
    CascadeNodeLink,
    SimulationClusterStatus,
    SimulationGridNode,
)
from ..serializers import (
    MythflowPlaybackSessionSerializer,
    SymbolicMilestoneLogSerializer,
    PersonalRitualGuideSerializer,
    SwarmReflectionThreadSerializer,
    SwarmReflectionPlaybackLogSerializer,
    PromptCascadeLogSerializer,
    CascadeNodeLinkSerializer,
    SimulationClusterStatusSerializer,
    SimulationGridNodeSerializer,
)


class MythflowPlaybackSessionViewSet(viewsets.ModelViewSet):
    queryset = MythflowPlaybackSession.objects.all().order_by("-created_at")
    serializer_class = MythflowPlaybackSessionSerializer


class SymbolicMilestoneLogViewSet(viewsets.ModelViewSet):
    queryset = SymbolicMilestoneLog.objects.all().order_by("-created_at")
    serializer_class = SymbolicMilestoneLogSerializer


class PersonalRitualGuideViewSet(viewsets.ModelViewSet):
    queryset = PersonalRitualGuide.objects.all().order_by("-created_at")
    serializer_class = PersonalRitualGuideSerializer


class SwarmReflectionThreadViewSet(viewsets.ModelViewSet):
    queryset = SwarmReflectionThread.objects.all().order_by("-created_at")
    serializer_class = SwarmReflectionThreadSerializer


class SwarmReflectionPlaybackLogViewSet(viewsets.ModelViewSet):
    queryset = SwarmReflectionPlaybackLog.objects.all().order_by("-created_at")
    serializer_class = SwarmReflectionPlaybackLogSerializer


class PromptCascadeLogViewSet(viewsets.ModelViewSet):
    queryset = PromptCascadeLog.objects.all().order_by("-created_at")
    serializer_class = PromptCascadeLogSerializer


class CascadeNodeLinkViewSet(viewsets.ModelViewSet):
    queryset = CascadeNodeLink.objects.all().order_by("-created_at")
    serializer_class = CascadeNodeLinkSerializer


class SimulationClusterStatusViewSet(viewsets.ModelViewSet):
    queryset = SimulationClusterStatus.objects.all().order_by("-created_at")
    serializer_class = SimulationClusterStatusSerializer


class SimulationGridNodeViewSet(viewsets.ModelViewSet):
    queryset = SimulationGridNode.objects.all().order_by("-created_at")
    serializer_class = SimulationGridNodeSerializer
