from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.models.project import AssistantProject
from project.models.core import Project
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

class Command(BaseCommand):
    help = "Delete stale assistant projects with no activity"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        identifier = options["assistant"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
            return
        cutoff = timezone.now() - timedelta(minutes=30)

        projects = (
            AssistantProject.objects.filter(assistant=assistant, created_at__lt=cutoff)
            .annotate(task_count=Count("project_tasks"), obj_count=Count("objectives"))
        )

        removed = 0
        for project in projects:
            if project.task_count or project.obj_count:
                continue
            has_memories = MemoryEntry.objects.filter(related_project__assistant_project=project).exists()
            has_reflections = AssistantReflectionLog.objects.filter(project=project).exists()
            if not has_memories and not has_reflections:
                Project.objects.filter(assistant_project=project).update(assistant_project=None)
                project.delete()
                removed += 1
        self.stdout.write(f"Removed {removed} stale projects for {assistant.slug}")
