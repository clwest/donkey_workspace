# intel_core/serializers.py

from rest_framework import serializers
from intel_core.models import (
    Document,
    DocumentFavorite,
    DocumentSet,
    DocumentChunk,
    EmbeddingMetadata,
)


class DocumentSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    token_count = serializers.IntegerField(source="token_count_int", read_only=True)
    chunk_count = serializers.SerializerMethodField()
    num_embedded = serializers.SerializerMethodField()
    glossary_ids = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "user",
            "title",
            "content",
            "description",
            "summary",
            "source_url",
            "source_type",
            "created_at",
            "metadata",
            "token_count",
            "chunk_count",
            "num_embedded",
            "glossary_ids",
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

    def get_chunk_count(self, obj):
        return obj.chunks.count()

    def get_num_embedded(self, obj):
        return obj.chunks.filter(embedding__isnull=False).count()

    def get_glossary_ids(self, obj):
        return list(obj.chunks.filter(is_glossary=True).values_list("id", flat=True))


class DocumentSetSerializer(serializers.ModelSerializer):

    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentSet
        fields = [
            "id",
            "title",
            "description",
            "documents",
            "created_at",
            "embedding_index",
        ]


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = "__all__"


class EmbeddingMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbeddingMetadata
        fields = "__all__"
