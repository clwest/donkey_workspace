from rest_framework import permissions
import logging
from .models import Project

logger = logging.getLogger(__name__)


class HasProjectAccess(permissions.BasePermission):
    """Allow access to project owners, assigned participants, team assistants, or superusers."""

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id") or view.kwargs.get("pk")
        if not project_id:
            return False
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return False

        if project.user == request.user or request.user.is_superuser:
            return True
        if project.participants.filter(id=request.user.id).exists():
            return True
        if project.team.filter(created_by=request.user).exists():
            return True
        if project.assistant and project.assistant.created_by == request.user:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user or request.user.is_superuser:
            return True
        if obj.participants.filter(id=request.user.id).exists():
            return True
        if obj.team.filter(created_by=request.user).exists():
            return True
        if obj.assistant and obj.assistant.created_by == request.user:
            return True
        logger.warning(
            "[ProjectAccess] Denied user %s for project %s", request.user.id, obj.id
        )
        return False
