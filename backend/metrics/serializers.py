from rest_framework import serializers
from .models import RitualPerformanceMetric


class RitualPerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = RitualPerformanceMetric
        fields = "__all__"
