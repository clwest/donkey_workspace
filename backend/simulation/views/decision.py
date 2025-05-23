from rest_framework import viewsets
from ..models import MemoryDecisionTreeNode
from ..serializers import MemoryDecisionTreeNodeSerializer


class MemoryDecisionTreeNodeViewSet(viewsets.ModelViewSet):
    queryset = MemoryDecisionTreeNode.objects.all().order_by("-created_at")
    serializer_class = MemoryDecisionTreeNodeSerializer
