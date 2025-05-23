from rest_framework import serializers
from .models import (
    CinemythStoryline,
    MythcastingChannel,
    AudienceFeedbackLoop,
    ParticipatoryStreamEvent,
)


class CinemythStorylineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemythStoryline
        fields = "__all__"


class MythcastingChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MythcastingChannel
        fields = "__all__"


class AudienceFeedbackLoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudienceFeedbackLoop
        fields = "__all__"


class ParticipatoryStreamEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipatoryStreamEvent
        fields = "__all__"
