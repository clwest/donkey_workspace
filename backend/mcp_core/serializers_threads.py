from rest_framework import serializers

from mcp_core.models import ThreadDiagnosticLog


class ThreadDiagnosticLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreadDiagnosticLog
        fields = [
            "id",
            "thread",
            "type",
            "score",
            "summary",
            "proposed_changes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
