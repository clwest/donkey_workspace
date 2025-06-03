# intel_core/serializers.py

from rest_framework import serializers
from intel_core.models import (
    Document,
    DocumentFavorite,
    DocumentSet,
    DocumentChunk,
    EmbeddingMetadata,
)
from prompts.utils.token_helpers import count_tokens


class DocumentSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    token_count = serializers.SerializerMethodField()
    chunk_count = serializers.SerializerMethodField()
    num_embedded = serializers.SerializerMethodField()
    embedded_chunks = serializers.SerializerMethodField()
    skipped_chunks = serializers.SerializerMethodField()
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
            "updated_at",
            "last_reflected_at",
            "metadata",
            "token_count",
            "chunk_count",
            "num_embedded",
            "embedded_chunks",
            "skipped_chunks",
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

    def get_token_count(self, obj):
        if obj.token_count_int:
            return obj.token_count_int
        meta_count = (
            obj.metadata.get("token_count") if isinstance(obj.metadata, dict) else None
        )
        if isinstance(meta_count, int):
            return meta_count
        return count_tokens(obj.content)

    def get_chunk_count(self, obj):
        meta_count = (
            obj.metadata.get("chunk_count") if isinstance(obj.metadata, dict) else None
        )
        if isinstance(meta_count, int):
            return meta_count
        return obj.chunks.count()

    def get_num_embedded(self, obj):
        return self.get_embedded_chunks(obj)

    def get_embedded_chunks(self, obj):
        meta_embedded = (
            obj.metadata.get("embedded_chunks")
            if isinstance(obj.metadata, dict)
            else None
        )
        if isinstance(meta_embedded, int):
            return meta_embedded
        return obj.chunks.filter(embedding__isnull=False).count()

    def get_skipped_chunks(self, obj):
        return obj.chunks.filter(embedding_status="skipped").count()

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


class DocumentChunkFullSerializer(serializers.ModelSerializer):
    """Full representation used by the admin-facing viewset."""

    class Meta:
        model = DocumentChunk
        fields = "__all__"


class DocumentChunkSerializer(serializers.ModelSerializer):
    embedding_id = serializers.SerializerMethodField()
    skipped = serializers.SerializerMethodField()

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "tokens",
            "score",
            "force_embed",
            "skipped",
            "embedding_id",
        ]

    def get_embedding_id(self, obj):
        return getattr(obj.embedding, "embedding_id", None)

    def get_skipped(self, obj):
        return obj.embedding_status == "skipped"


class DocumentChunkInfoSerializer(serializers.ModelSerializer):
    embedding_id = serializers.SerializerMethodField()
    skipped = serializers.SerializerMethodField()
    token_count = serializers.IntegerField(source="tokens", read_only=True)
    embedding_status = serializers.CharField(read_only=True)

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "order",
            "text",
            "score",
            "token_count",
            "force_embed",
            "skipped",
            "embedding_id",
            "embedding_status",
        ]

    def get_embedding_id(self, obj):
        return getattr(obj.embedding, "embedding_id", None)

    def get_skipped(self, obj):
        return obj.embedding_status == "skipped"


class DocumentDetailSerializer(DocumentSerializer):
    embedded_chunks = serializers.SerializerMethodField()
    skipped_chunks = serializers.SerializerMethodField()

    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ["embedded_chunks", "skipped_chunks"]

    def get_embedded_chunks(self, obj):
        return obj.chunks.filter(embedding__isnull=False).count()

    def get_skipped_chunks(self, obj):
        return obj.chunks.filter(embedding_status="skipped").count()


class EmbeddingMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmbeddingMetadata
        fields = "__all__"
