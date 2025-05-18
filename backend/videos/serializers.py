# runway/serializers.py

from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "user",
            "prompt",
            "theme",
            "tags",
            "status",
            "input_image",
            "video_url",
            "video_file",
            "provider",
            "model_backend",
            "prediction_id",
            "created_at",
            "updated_at",
            "completed_at",
            "paragraph_index",
        ]
        read_only_fields = [
            "status",
            "created_at",
            "updated_at",
            "completed_at",
            "user",
            "provider",
            "video_file",
            "prediction_id",
        ]

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video_file and hasattr(obj.video_file, "url"):
            return (
                request.build_absolute_uri(obj.video_file.url)
                if request
                else obj.video_file.url
            )
        return obj.video_url  # fallback if video_url is stored from external sources
