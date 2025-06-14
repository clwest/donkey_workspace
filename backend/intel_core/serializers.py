# intel_core/serializers.py

from rest_framework import serializers
from intel_core.models import (
    Document,
    DocumentFavorite,
    DocumentSet,
    DocumentChunk,
    EmbeddingMetadata,
)
from assistants.models.reflection import AssistantReflectionLog
from assistants.serializers import TagSerializer
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
    progress_status = serializers.SerializerMethodField()
    progress_error = serializers.SerializerMethodField()
    failed_chunks = serializers.SerializerMethodField()
    chunk_index = serializers.SerializerMethodField()
    system_prompt_id = serializers.SerializerMethodField()
    reflection_prompt_id = serializers.SerializerMethodField()
    reflection_prompt_title = serializers.SerializerMethodField()
    upload_status = serializers.CharField(read_only=True)
    upload_error = serializers.CharField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    memory_context = serializers.UUIDField(source="memory_context_id", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "user",
            "memory_context",
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
            "progress_status",
            "progress_error",
            "upload_status",
            "upload_error",
            "failed_chunks",
            "chunk_index",
            "system_prompt_id",
            "reflection_prompt_id",
            "reflection_prompt_title",
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

    def _get_progress(self, obj):
        progress_id = None
        if isinstance(obj.metadata, dict):
            progress_id = obj.metadata.get("progress_id")
        if progress_id:
            from intel_core.models import DocumentProgress

            return DocumentProgress.objects.filter(progress_id=progress_id).first()
        return None

    def get_progress_status(self, obj):
        prog = self._get_progress(obj)
        if prog:
            return prog.status
        return getattr(obj, "progress_status", None)

    def get_progress_error(self, obj):
        prog = self._get_progress(obj)
        if prog:
            return prog.error_message
        return getattr(obj, "progress_error", "")

    def get_failed_chunks(self, obj):
        prog = self._get_progress(obj)
        return prog.failed_chunks if prog else []

    def get_chunk_index(self, obj):
        prog = self._get_progress(obj)
        return prog.processed if prog else None

    def get_system_prompt_id(self, obj):
        prompt = getattr(obj, "generated_prompt", None)
        if prompt:
            return str(prompt.id)
        system_prompt = obj.prompts.filter(type="system").first()
        return str(system_prompt.id) if system_prompt else None

    def get_reflection_prompt_id(self, obj):
        prompt = getattr(obj, "generated_prompt", None)
        return str(prompt.id) if prompt else None

    def get_reflection_prompt_title(self, obj):
        prompt = getattr(obj, "generated_prompt", None)
        return prompt.title if prompt else None


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
    glossary_score = serializers.FloatField(read_only=True)
    glossary_boost = serializers.FloatField(read_only=True)
    is_glossary_weak = serializers.SerializerMethodField()

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "tokens",
            "score",
            "force_embed",
            "skipped",
            "embedding_id",
            "glossary_score",
            "glossary_boost",
            "is_glossary_weak",
        ]

    def get_embedding_id(self, obj):
        return getattr(obj.embedding, "id", None)

    def get_skipped(self, obj):
        return obj.embedding_status == "skipped"

    def get_is_glossary_weak(self, obj):
        from django.conf import settings

        threshold = getattr(settings, "GLOSSARY_WEAK_THRESHOLD", 0.2)
        return obj.glossary_score < threshold


class DocumentChunkInfoSerializer(serializers.ModelSerializer):
    embedding_id = serializers.SerializerMethodField()
    skipped = serializers.SerializerMethodField()
    token_count = serializers.IntegerField(source="tokens", read_only=True)
    matched_anchors = serializers.ListField(read_only=True)
    glossary_score = serializers.FloatField(read_only=True)
    glossary_boost = serializers.FloatField(read_only=True)
    is_glossary_weak = serializers.SerializerMethodField()
    embedding_status = serializers.CharField(read_only=True)

    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "order",
            "text",
            "score",
            "glossary_score",
            "glossary_boost",
            "is_glossary_weak",
            "token_count",
            "force_embed",
            "skipped",
            "matched_anchors",
            "embedding_id",
            "embedding_status",
        ]

    def get_embedding_id(self, obj):
        return getattr(obj.embedding, "id", None)

    def get_skipped(self, obj):
        return obj.embedding_status == "skipped"

    def get_is_glossary_weak(self, obj):
        from django.conf import settings

        threshold = getattr(settings, "GLOSSARY_WEAK_THRESHOLD", 0.2)
        return obj.glossary_score < threshold


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


class DocumentReflectionSerializer(serializers.ModelSerializer):
    assistant = serializers.StringRelatedField()
    assistant_slug = serializers.SlugField(source="assistant.slug", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = AssistantReflectionLog
        fields = [
            "id",
            "assistant",
            "assistant_slug",
            "created_at",
            "summary",
            "tags",
            "group_slug",
            "document_section",
            "is_summary",
        ]
