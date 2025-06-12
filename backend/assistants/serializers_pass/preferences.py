from rest_framework import serializers
from assistants.models.user_preferences import AssistantUserPreferences


class AssistantUserPreferencesSerializer(serializers.ModelSerializer):
    """Serialize AssistantUserPreferences."""

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AssistantUserPreferences
        fields = [
            "tone",
            "planning_mode",
            "custom_tags",
            "self_narration_enabled",
            "username",
        ]
