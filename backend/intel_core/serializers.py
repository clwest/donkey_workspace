# intel_core/serializers.py

from rest_framework import serializers
from intel_core.models import Document, DocumentFavorite


class DocumentSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "content",
            "description",
            "summary",
            "source_url",
            "source_type",
            "created_at",
            "metadata",
            "is_favorited",
            "tags",
        ]

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return DocumentFavorite.objects.filter(user=request.user, document=obj).exists()

    def get_tags(self, obj):
        return list(obj.tags.values_list("name", flat=True))
