from rest_framework import generics
from ..models import WorkflowDefinition, WorkflowExecutionLog
from ..serializers import WorkflowDefinitionSerializer, WorkflowExecutionLogSerializer


class WorkflowDefinitionListCreateView(generics.ListCreateAPIView):
    queryset = WorkflowDefinition.objects.all().order_by("-created_at")
    serializer_class = WorkflowDefinitionSerializer


class WorkflowExecutionLogListView(generics.ListAPIView):
    queryset = WorkflowExecutionLog.objects.all().order_by("-created_at")
    serializer_class = WorkflowExecutionLogSerializer
