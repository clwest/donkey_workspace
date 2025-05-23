from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import (
    CinemythStoryline,
    MythcastingChannel,
    AudienceFeedbackLoop,
    ParticipatoryStreamEvent,
)
from .serializers import (
    CinemythStorylineSerializer,
    MythcastingChannelSerializer,
    AudienceFeedbackLoopSerializer,
    ParticipatoryStreamEventSerializer,
)


class CinemythStorylineViewSet(viewsets.ModelViewSet):
    queryset = CinemythStoryline.objects.all().order_by("-created_at")
    serializer_class = CinemythStorylineSerializer
    permission_classes = [AllowAny]


class MythcastingChannelViewSet(viewsets.ModelViewSet):
    queryset = MythcastingChannel.objects.all().order_by("-created_at")
    serializer_class = MythcastingChannelSerializer
    permission_classes = [AllowAny]


class AudienceFeedbackLoopViewSet(viewsets.ModelViewSet):
    queryset = AudienceFeedbackLoop.objects.all().order_by("-created_at")
    serializer_class = AudienceFeedbackLoopSerializer
    permission_classes = [AllowAny]


class ParticipatoryStreamEventViewSet(viewsets.ModelViewSet):
    queryset = ParticipatoryStreamEvent.objects.all().order_by("-created_at")
    serializer_class = ParticipatoryStreamEventSerializer
    permission_classes = [AllowAny]
