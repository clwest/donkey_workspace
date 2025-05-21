from celery import shared_task
from django.db import models
from django.utils import timezone

from mcp_core.models import NarrativeThread
from project.models import Project, ProjectMilestone

@shared_task
def update_thread_progress(thread_id: str):
    try:
        thread = NarrativeThread.objects.get(id=thread_id)
    except NarrativeThread.DoesNotExist:
        return "not found"

    projects = Project.objects.filter(
        models.Q(thread=thread) | models.Q(narrative_thread=thread)
    )
    milestones = ProjectMilestone.objects.filter(project__in=projects)

    total = milestones.count()
    completed = [
        str(m.id)
        for m in milestones
        if getattr(m, "status", "") == "Completed" or getattr(m, "is_completed", False)
    ]
    completed_count = len(completed)
    progress_percent = int((completed_count / total) * 100) if total else 0

    status = NarrativeThread.CompletionStatus.DRAFT
    if total:
        status = NarrativeThread.CompletionStatus.IN_PROGRESS
        if completed_count == total:
            status = NarrativeThread.CompletionStatus.COMPLETED
            if not thread.completed_at:
                thread.completed_at = timezone.now()

    thread.completed_milestones = completed
    thread.progress_percent = progress_percent
    thread.completion_status = status
    thread.save(
        update_fields=[
            "completed_milestones",
            "progress_percent",
            "completion_status",
            "completed_at",
        ]
    )
    return "ok"

@shared_task
def sync_all_thread_progress():
    for thread in NarrativeThread.objects.all():
        update_thread_progress(thread.id)
    return "done"
