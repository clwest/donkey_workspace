# trainers/serializers.py
from rest_framework import serializers
from .models import ReplicateModel, ReplicatePrediction


class ReplicateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplicateModel
        fields = [
            "id",
            "name",
            "version",
            "description",
            "is_active",
            "created_at",
        ]


class ReplicatePredictionSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source="model.name", read_only=True)
    model_version = serializers.CharField(source="model.version", read_only=True)

    class Meta:
        model = ReplicatePrediction
        fields = [
            "id",
            "user",
            "model",
            "model_name",
            "model_version",
            "prediction_id",
            "prompt",
            "status",
            "num_outputs",
            "files",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = ["user", "files"]
