from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from prompts.models import (
    Prompt,
    PromptPreferences,
    PromptUsageTemplate,
    PromptCapsule,
    CapsuleTransferLog,
)
from assistants.models.assistant import Assistant
from mcp_core.models import Tag
from mcp_core.serializers_tags import TagSerializer


class PromptSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Prompt
        fields = "__all__"

    def create(self, validated_data):
        tag_values = self.initial_data.get("tags", [])
        prompt = Prompt.objects.create(**validated_data)

        for tag in tag_values:
            tag_obj, _ = Tag.objects.get_or_create(name=tag.strip())
            prompt.tags.add(tag_obj)

        from prompts.utils.embeddings import get_prompt_embedding
        from embeddings.helpers.helpers_io import save_embedding

        embedding = get_prompt_embedding(prompt.content)
        prompt.embedding = embedding
        prompt.save()
        save_embedding(prompt, embedding)
        return prompt

    def update(self, instance, validated_data):
        tag_values = self.initial_data.get("tags", [])
        instance = super().update(instance, validated_data)

        instance.tags.clear()
        for tag in tag_values:
            tag_obj, _ = Tag.objects.get_or_create(name=tag.strip())
            instance.tags.add(tag_obj)

        if "content" in validated_data:
            from prompts.utils.embeddings import get_prompt_embedding
            from embeddings.helpers.helpers_io import save_embedding

            embedding = get_prompt_embedding(instance.content)
            instance.embedding = embedding
            instance.save()
            save_embedding(instance, embedding)

        return instance


class PromptPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptPreferences
        fields = "__all__"


class PromptCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = [
            "title",
            "slug",
            "content",
            "type",
            "source",
            "tone",
            "tags",
            "is_draft",
        ]
        read_only_fields = ["slug"]


class PromptAssignAssistantSerializer(serializers.Serializer):
    assistant_id = serializers.UUIDField()

    def validate_assistant_id(self, value):
        from utils.resolvers import resolve_or_error
        from django.core.exceptions import ObjectDoesNotExist

        try:
            assistant = resolve_or_error(str(value), Assistant)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(_("Assistant not found."))
        return assistant

    def save(self, **kwargs):
        prompt = self.context["prompt"]
        assistant = self.validated_data["assistant_id"]
        assistant.system_prompt = prompt
        assistant.save()
        return assistant


class PromptMutationRequestSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(
        choices=["clarify", "shorten", "expand", "formal", "casual", "remix"]
    )


class PromptUsageTemplateSerializer(serializers.ModelSerializer):
    prompt = PromptSerializer(read_only=True)

    class Meta:
        model = PromptUsageTemplate
        fields = [
            "id",
            "title",
            "description",
            "prompt",
            "example_input",
            "example_output",
        ]


class AssistantMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = ["id", "name", "slug"]


class PromptCapsuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptCapsule
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CapsuleTransferLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapsuleTransferLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
