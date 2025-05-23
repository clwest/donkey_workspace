from rest_framework import viewsets
from ..models import SymbolicAuthorityTransferLog
from ..serializers import SymbolicAuthorityTransferLogSerializer


class SymbolicAuthorityTransferLogViewSet(viewsets.ModelViewSet):
    queryset = SymbolicAuthorityTransferLog.objects.all().order_by("-created_at")
    serializer_class = SymbolicAuthorityTransferLogSerializer
