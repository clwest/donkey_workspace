"""Viewsets providing API endpoints for working with ``Project`` objects."""

from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class ProjectViewSet(viewsets.ModelViewSet):
    """CRUD operations for :class:`Project` instances returned as JSON."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
