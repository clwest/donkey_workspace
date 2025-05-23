from rest_framework import viewsets
from ..models import ReflectiveTheaterSession
from ..serializers import ReflectiveTheaterSessionSerializer


class ReflectiveTheaterSessionViewSet(viewsets.ModelViewSet):
    queryset = ReflectiveTheaterSession.objects.all().order_by("-created_at")
    serializer_class = ReflectiveTheaterSessionSerializer
