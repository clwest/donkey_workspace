from rest_framework import serializers
from .models import AdaptiveLoopConfig


class AdaptiveLoopConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdaptiveLoopConfig
        fields = "__all__"
