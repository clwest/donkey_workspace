from django.core.management.base import BaseCommand
from project.models import Project
from assistants.helpers.collaboration import evaluate_team_alignment


class Command(BaseCommand):
    help = "Evaluate collaboration styles for all projects"

    def handle(self, *args, **options):
        for project in Project.objects.all():
            log = evaluate_team_alignment(project.id)
            if log and log.style_conflict_detected:
                self.stdout.write(self.style.WARNING(f"Conflict on {project.title}"))
        self.stdout.write(self.style.SUCCESS("Evaluation complete"))
