from rest_framework import serializers
from .models import FeedbackEntry


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackEntry
        fields = [
            "id",
            "user",
            "assistant_slug",
            "category",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]
