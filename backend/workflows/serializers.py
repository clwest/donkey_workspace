from rest_framework import serializers
from .models import WorkflowDefinition, WorkflowExecutionLog


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowDefinition
        fields = "__all__"


class WorkflowExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowExecutionLog
        fields = "__all__"
