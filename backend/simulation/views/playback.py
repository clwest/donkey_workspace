from rest_framework import viewsets
from ..models import (
    MythflowPlaybackSession,
    SymbolicMilestoneLog,
    PersonalRitualGuide,
)
from ..serializers import (
    MythflowPlaybackSessionSerializer,
    SymbolicMilestoneLogSerializer,
    PersonalRitualGuideSerializer,
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
