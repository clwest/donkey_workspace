from rest_framework import viewsets
from ..models import SymbolicDialogueScript
from ..serializers import SymbolicDialogueScriptSerializer


class SymbolicDialogueScriptViewSet(viewsets.ModelViewSet):
    queryset = SymbolicDialogueScript.objects.all().order_by("-created_at")
    serializer_class = SymbolicDialogueScriptSerializer
