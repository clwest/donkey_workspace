from rest_framework import viewsets
from ..models import NarrativeMutationTrace
from ..serializers import NarrativeMutationTraceSerializer


class NarrativeMutationTraceViewSet(viewsets.ModelViewSet):
    queryset = NarrativeMutationTrace.objects.all().order_by("-created_at")
    serializer_class = NarrativeMutationTraceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        assistant = self.request.GET.get("assistant")
        if assistant:
            qs = qs.filter(assistant_id=assistant)
        return qs
