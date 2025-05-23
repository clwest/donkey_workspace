from rest_framework import serializers
from .models import LearningTrailNode


class LearningTrailNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningTrailNode
        fields = "__all__"
