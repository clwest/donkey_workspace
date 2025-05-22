"""Service layer for project-related operations."""

from django.shortcuts import get_object_or_404
from typing import Optional
from django.contrib.auth.models import AbstractBaseUser

from assistants.models.assistant import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.helpers.team_memory import assign_project_role, get_visible_memories
from project.models.core import Project


def user_can_access_project(user: Optional[AbstractBaseUser], project: Project) -> bool:
    """Return True if ``user`` can access ``project``."""
    if project.is_public:
        return True
    if not user or not user.is_authenticated:
        return False
    if (
        user == project.user
        or user.is_staff
        or project.participants.filter(id=user.id).exists()
    ):
        return True
    return False


def assign_role_to_assistant(project: Project, assistant_id: str, role: str) -> None:
    """Assign a role to an assistant for the given project."""
    assistant = get_object_or_404(Assistant, id=assistant_id)
    assign_project_role(assistant, project, role)


def fetch_team_memories(project: Project, assistant_id: Optional[str] = None):
    """Return visible memory entries for the project and optional assistant."""
    assistant = None
    if assistant_id:
        assistant = get_object_or_404(Assistant, id=assistant_id)
    return get_visible_memories(project, assistant)


def fetch_team_reflections(project: Project):
    """Return reflection logs linked to ``project``."""
    return AssistantReflectionLog.objects.filter(
        project__linked_projects=project
    ).order_by("-created_at")
