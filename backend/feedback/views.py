from rest_framework import viewsets, permissions
from .models import FeedbackEntry
from .serializers import FeedbackSerializer


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = FeedbackEntry.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
