from django.shortcuts import get_object_or_404

from project.models import Project
from mcp_core.models import NarrativeThread


class AssistantService:
    """Helper service for assistant-related database access."""

    @staticmethod
    def get_project(project_id):
        return Project.objects.filter(id=project_id).first()

    @staticmethod
    def get_project_or_404(project_id):
        return get_object_or_404(Project, id=project_id)

    @staticmethod
    def create_project(**kwargs):
        return Project.objects.create(**kwargs)

    @staticmethod
    def project_for_assistant(assistant):
        return Project.objects.filter(assistant=assistant).first()

    @staticmethod
    def get_thread(thread_id):
        return NarrativeThread.objects.filter(id=thread_id).first()

    @staticmethod
    def get_thread_or_404(thread_id):
        return get_object_or_404(NarrativeThread, id=thread_id)
